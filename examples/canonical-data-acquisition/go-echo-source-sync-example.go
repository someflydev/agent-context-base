package acquisition

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"time"

	"github.com/labstack/echo/v4"
)

const (
	SourceName     = "github-releases"
	AdapterVersion = "github-releases-v1"
)

type SyncCursor struct {
	Owner       string `json:"owner"`
	Repo        string `json:"repo"`
	Page        int    `json:"page"`
	ETag        string `json:"etag,omitempty"`
	MaxAttempts int    `json:"maxAttempts,omitempty"`
}

func (cursor SyncCursor) CheckpointToken() string {
	if cursor.ETag != "" {
		return cursor.ETag
	}
	return fmt.Sprintf("page=%d", cursor.Page)
}

type FetchResult struct {
	Body            []byte
	FetchedAt       time.Time
	StatusCode      int
	ContentType     string
	RequestURL      string
	CheckpointToken string
	NextPage        *int
}

type RawCapture struct {
	SourceName      string `json:"sourceName"`
	Owner           string `json:"owner"`
	Repo            string `json:"repo"`
	FetchedAt       string `json:"fetchedAt"`
	RawPath         string `json:"rawPath"`
	MetadataPath    string `json:"metadataPath"`
	SHA256          string `json:"sha256"`
	CheckpointToken string `json:"checkpointToken"`
	RequestURL      string `json:"requestUrl"`
}

type ReleaseProvenance struct {
	SourceName      string `json:"sourceName"`
	RawPath         string `json:"rawPath"`
	FetchedAt       string `json:"fetchedAt"`
	SHA256          string `json:"sha256"`
	CheckpointToken string `json:"checkpointToken"`
	AdapterVersion  string `json:"adapterVersion"`
}

type NormalizedRelease struct {
	CanonicalID string            `json:"canonicalId"`
	SourceID    int64             `json:"sourceId"`
	Owner       string            `json:"owner"`
	Repo        string            `json:"repo"`
	TagName     string            `json:"tagName"`
	Title       string            `json:"title"`
	PublishedAt string            `json:"publishedAt"`
	HTMLURL     string            `json:"htmlUrl"`
	Provenance  ReleaseProvenance `json:"provenance"`
}

type SyncResult struct {
	RawCapture RawCapture          `json:"rawCapture"`
	Records    []NormalizedRelease `json:"records"`
	NextCursor *SyncCursor         `json:"nextCursor,omitempty"`
}

type SyncReceipt struct {
	SourceName      string `json:"sourceName"`
	RawPath         string `json:"rawPath"`
	NormalizedCount int    `json:"normalizedCount"`
	CheckpointToken string `json:"checkpointToken"`
	NextPage        *int   `json:"nextPage,omitempty"`
}

type SourceAdapter interface {
	FetchReleasePage(ctx context.Context, cursor SyncCursor) (FetchResult, error)
}

type RetryableError struct {
	Message string
}

func (err RetryableError) Error() string {
	return err.Message
}

type GitHubReleaseAdapter struct {
	Client *http.Client
}

func (adapter GitHubReleaseAdapter) FetchReleasePage(ctx context.Context, cursor SyncCursor) (FetchResult, error) {
	values := url.Values{}
	values.Set("per_page", "50")
	values.Set("page", fmt.Sprintf("%d", maxInt(cursor.Page, 1)))
	requestURL := fmt.Sprintf(
		"https://api.github.com/repos/%s/%s/releases?%s",
		url.PathEscape(cursor.Owner),
		url.PathEscape(cursor.Repo),
		values.Encode(),
	)

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, requestURL, nil)
	if err != nil {
		return FetchResult{}, err
	}
	req.Header.Set("Accept", "application/vnd.github+json")
	req.Header.Set("User-Agent", "agent-context-base-canonical-example")
	req.Header.Set("X-GitHub-Api-Version", "2022-11-28")
	if cursor.ETag != "" {
		req.Header.Set("If-None-Match", cursor.ETag)
	}

	client := adapter.Client
	if client == nil {
		client = http.DefaultClient
	}

	resp, err := client.Do(req)
	if err != nil {
		return FetchResult{}, RetryableError{Message: "transient upstream network failure"}
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusTooManyRequests || resp.StatusCode >= http.StatusInternalServerError {
		return FetchResult{}, RetryableError{Message: fmt.Sprintf("retryable upstream status %d", resp.StatusCode)}
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return FetchResult{}, err
	}

	var nextPage *int
	if len(body) > 0 {
		candidate := maxInt(cursor.Page, 1) + 1
		nextPage = &candidate
	}

	checkpointToken := resp.Header.Get("ETag")
	if checkpointToken == "" {
		checkpointToken = cursor.CheckpointToken()
	}

	return FetchResult{
		Body:            body,
		FetchedAt:       time.Now().UTC(),
		StatusCode:      resp.StatusCode,
		ContentType:     resp.Header.Get("Content-Type"),
		RequestURL:      requestURL,
		CheckpointToken: checkpointToken,
		NextPage:        nextPage,
	}, nil
}

type githubReleasePayload struct {
	ID          int64  `json:"id"`
	TagName     string `json:"tag_name"`
	Name        string `json:"name"`
	HTMLURL     string `json:"html_url"`
	PublishedAt string `json:"published_at"`
	Draft       bool   `json:"draft"`
}

func archiveRawCapture(archiveRoot string, cursor SyncCursor, fetchResult FetchResult) (RawCapture, error) {
	captureDir := filepath.Join(
		archiveRoot,
		SourceName,
		cursor.Owner,
		cursor.Repo,
		fetchResult.FetchedAt.Format("2006/01/02/150405Z"),
	)
	if err := os.MkdirAll(captureDir, 0o755); err != nil {
		return RawCapture{}, err
	}

	rawPath := filepath.Join(captureDir, fmt.Sprintf("page-%d.json", maxInt(cursor.Page, 1)))
	metadataPath := filepath.Join(captureDir, fmt.Sprintf("page-%d.metadata.json", maxInt(cursor.Page, 1)))
	if err := os.WriteFile(rawPath, fetchResult.Body, 0o644); err != nil {
		return RawCapture{}, err
	}

	sum := sha256.Sum256(fetchResult.Body)
	capture := RawCapture{
		SourceName:      SourceName,
		Owner:           cursor.Owner,
		Repo:            cursor.Repo,
		FetchedAt:       fetchResult.FetchedAt.Format(time.RFC3339),
		RawPath:         rawPath,
		MetadataPath:    metadataPath,
		SHA256:          hex.EncodeToString(sum[:]),
		CheckpointToken: fetchResult.CheckpointToken,
		RequestURL:      fetchResult.RequestURL,
	}

	metadataBytes, err := json.MarshalIndent(capture, "", "  ")
	if err != nil {
		return RawCapture{}, err
	}
	if err := os.WriteFile(metadataPath, metadataBytes, 0o644); err != nil {
		return RawCapture{}, err
	}
	return capture, nil
}

func parseArchivedReleasePayload(rawCapture RawCapture) ([]githubReleasePayload, error) {
	body, err := os.ReadFile(rawCapture.RawPath)
	if err != nil {
		return nil, err
	}

	var payload []githubReleasePayload
	if err := json.Unmarshal(body, &payload); err != nil {
		return nil, err
	}
	return payload, nil
}

func normalizeReleaseRecords(rawCapture RawCapture, payload []githubReleasePayload) []NormalizedRelease {
	provenance := ReleaseProvenance{
		SourceName:      rawCapture.SourceName,
		RawPath:         rawCapture.RawPath,
		FetchedAt:       rawCapture.FetchedAt,
		SHA256:          rawCapture.SHA256,
		CheckpointToken: rawCapture.CheckpointToken,
		AdapterVersion:  AdapterVersion,
	}

	records := make([]NormalizedRelease, 0, len(payload))
	for _, item := range payload {
		if item.Draft {
			continue
		}
		title := item.Name
		if title == "" {
			title = item.TagName
		}
		records = append(records, NormalizedRelease{
			CanonicalID: fmt.Sprintf("%s:%s/%s:%d", SourceName, rawCapture.Owner, rawCapture.Repo, item.ID),
			SourceID:    item.ID,
			Owner:       rawCapture.Owner,
			Repo:        rawCapture.Repo,
			TagName:     item.TagName,
			Title:       title,
			PublishedAt: item.PublishedAt,
			HTMLURL:     item.HTMLURL,
			Provenance:  provenance,
		})
	}
	return records
}

type SyncService struct {
	Adapter     SourceAdapter
	ArchiveRoot string
}

func (service SyncService) SyncReleasePage(ctx context.Context, cursor SyncCursor) (SyncResult, error) {
	attempts := maxInt(cursor.MaxAttempts, 1)
	var fetchResult FetchResult
	var err error
	for attempt := 1; attempt <= attempts; attempt++ {
		fetchResult, err = service.Adapter.FetchReleasePage(ctx, cursor)
		if err == nil {
			break
		}
		var retryable RetryableError
		if !errors.As(err, &retryable) || attempt == attempts {
			return SyncResult{}, err
		}
	}

	rawCapture, err := archiveRawCapture(service.ArchiveRoot, cursor, fetchResult)
	if err != nil {
		return SyncResult{}, err
	}

	payload, err := parseArchivedReleasePayload(rawCapture)
	if err != nil {
		return SyncResult{}, err
	}

	var nextCursor *SyncCursor
	if fetchResult.NextPage != nil {
		nextCursor = &SyncCursor{
			Owner:       cursor.Owner,
			Repo:        cursor.Repo,
			Page:        *fetchResult.NextPage,
			ETag:        fetchResult.CheckpointToken,
			MaxAttempts: cursor.MaxAttempts,
		}
	}

	return SyncResult{
		RawCapture: rawCapture,
		Records:    normalizeReleaseRecords(rawCapture, payload),
		NextCursor: nextCursor,
	}, nil
}

func (service SyncService) ReplayFromArchive(rawCapture RawCapture) ([]NormalizedRelease, error) {
	payload, err := parseArchivedReleasePayload(rawCapture)
	if err != nil {
		return nil, err
	}
	return normalizeReleaseRecords(rawCapture, payload), nil
}

type SyncHandler struct {
	Service SyncService
}

func (handler SyncHandler) Register(group *echo.Group) {
	group.POST("/sources/github-releases/:owner/:repo/sync", handler.Run)
}

func (handler SyncHandler) Run(c echo.Context) error {
	cursor := SyncCursor{
		Owner:       c.Param("owner"),
		Repo:        c.Param("repo"),
		Page:        1,
		MaxAttempts: 2,
	}
	if err := c.Bind(&cursor); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid sync request")
	}
	if cursor.Page <= 0 {
		cursor.Page = 1
	}

	result, err := handler.Service.SyncReleasePage(c.Request().Context(), cursor)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadGateway, err.Error())
	}

	var nextPage *int
	if result.NextCursor != nil {
		nextPage = &result.NextCursor.Page
	}

	return c.JSON(http.StatusAccepted, SyncReceipt{
		SourceName:      SourceName,
		RawPath:         result.RawCapture.RawPath,
		NormalizedCount: len(result.Records),
		CheckpointToken: result.RawCapture.CheckpointToken,
		NextPage:        nextPage,
	})
}

func maxInt(value int, fallback int) int {
	if value < fallback {
		return fallback
	}
	return value
}
