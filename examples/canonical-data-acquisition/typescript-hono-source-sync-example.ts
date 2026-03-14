import { Hono } from "hono";

const SOURCE_NAME = "github-releases";
const ADAPTER_VERSION = "github-releases-v1";

export type SyncCursor = {
  owner: string;
  repo: string;
  page: number;
  etag?: string;
  maxAttempts?: number;
};

export type FetchResult = {
  body: Uint8Array;
  fetchedAt: string;
  statusCode: number;
  contentType: string;
  requestUrl: string;
  checkpointToken: string;
  nextPage?: number;
};

export type RawCapture = {
  sourceName: string;
  owner: string;
  repo: string;
  fetchedAt: string;
  rawPath: string;
  metadataPath: string;
  sha256: string;
  checkpointToken: string;
  requestUrl: string;
};

export type ReleaseProvenance = {
  sourceName: string;
  rawPath: string;
  fetchedAt: string;
  sha256: string;
  checkpointToken: string;
  adapterVersion: string;
};

export type NormalizedReleaseRecord = {
  canonicalId: string;
  sourceId: number;
  owner: string;
  repo: string;
  tagName: string;
  title: string;
  publishedAt: string;
  htmlUrl: string;
  provenance: ReleaseProvenance;
};

export type SyncResult = {
  rawCapture: RawCapture;
  records: NormalizedReleaseRecord[];
  nextCursor?: SyncCursor;
};

export interface SourceAdapter {
  fetchReleasePage(cursor: SyncCursor): Promise<FetchResult>;
}

type GitHubReleasePayload = {
  id: number;
  tag_name: string;
  name?: string;
  html_url: string;
  published_at?: string;
  draft?: boolean;
};

export class RetryableFetchError extends Error {}

export class GitHubReleaseAdapter implements SourceAdapter {
  async fetchReleasePage(cursor: SyncCursor): Promise<FetchResult> {
    const page = Math.max(cursor.page, 1);
    const requestUrl = new URL(
      `https://api.github.com/repos/${cursor.owner}/${cursor.repo}/releases`,
    );
    requestUrl.searchParams.set("per_page", "50");
    requestUrl.searchParams.set("page", String(page));

    const response = await fetch(requestUrl, {
      headers: {
        Accept: "application/vnd.github+json",
        "User-Agent": "agent-context-base-canonical-example",
        "X-GitHub-Api-Version": "2022-11-28",
        ...(cursor.etag ? { "If-None-Match": cursor.etag } : {}),
      },
    });

    if (response.status === 429 || response.status >= 500) {
      throw new RetryableFetchError(`retryable upstream status ${response.status}`);
    }

    return {
      body: new Uint8Array(await response.arrayBuffer()),
      fetchedAt: new Date().toISOString(),
      statusCode: response.status,
      contentType: response.headers.get("content-type") ?? "application/json",
      requestUrl: requestUrl.toString(),
      checkpointToken:
        response.headers.get("etag") ?? cursor.etag ?? `page=${page}`,
      nextPage: response.status === 304 ? undefined : page + 1,
    };
  }
}

export async function archiveRawCapture(
  archiveRoot: string,
  cursor: SyncCursor,
  fetchResult: FetchResult,
): Promise<RawCapture> {
  const stamp = fetchResult.fetchedAt
    .replace(/[-:]/g, "")
    .replace(/\.\d+Z$/, "Z")
    .replace("T", "/")
    .replace("Z", "Z");
  const baseDir = `${archiveRoot}/${SOURCE_NAME}/${cursor.owner}/${cursor.repo}/${stamp}`;
  const page = Math.max(cursor.page, 1);
  const rawPath = `${baseDir}/page-${page}.json`;
  const metadataPath = `${baseDir}/page-${page}.metadata.json`;
  const sha256 = await sha256Hex(fetchResult.body);

  const capture: RawCapture = {
    sourceName: SOURCE_NAME,
    owner: cursor.owner,
    repo: cursor.repo,
    fetchedAt: fetchResult.fetchedAt,
    rawPath,
    metadataPath,
    sha256,
    checkpointToken: fetchResult.checkpointToken,
    requestUrl: fetchResult.requestUrl,
  };

  await Bun.write(rawPath, fetchResult.body);
  await Bun.write(metadataPath, JSON.stringify(capture, null, 2));
  return capture;
}

export async function parseArchivedReleasePayload(
  rawCapture: RawCapture,
): Promise<GitHubReleasePayload[]> {
  const text = await Bun.file(rawCapture.rawPath).text();
  return JSON.parse(text) as GitHubReleasePayload[];
}

export function normalizeReleaseRecords(
  rawCapture: RawCapture,
  payload: GitHubReleasePayload[],
): NormalizedReleaseRecord[] {
  const provenance: ReleaseProvenance = {
    sourceName: rawCapture.sourceName,
    rawPath: rawCapture.rawPath,
    fetchedAt: rawCapture.fetchedAt,
    sha256: rawCapture.sha256,
    checkpointToken: rawCapture.checkpointToken,
    adapterVersion: ADAPTER_VERSION,
  };

  return payload
    .filter((item) => !item.draft)
    .sort((left, right) => right.published_at?.localeCompare(left.published_at ?? "") ?? 0)
    .map((item) => ({
      canonicalId: `${SOURCE_NAME}:${rawCapture.owner}/${rawCapture.repo}:${item.id}`,
      sourceId: item.id,
      owner: rawCapture.owner,
      repo: rawCapture.repo,
      tagName: item.tag_name,
      title: item.name ?? item.tag_name,
      publishedAt: item.published_at ?? "",
      htmlUrl: item.html_url,
      provenance,
    }));
}

export class GitHubReleaseSyncService {
  constructor(
    private readonly adapter: SourceAdapter,
    private readonly archiveRoot: string,
  ) {}

  async syncReleasePage(cursor: SyncCursor): Promise<SyncResult> {
    const attempts = Math.max(cursor.maxAttempts ?? 2, 1);
    let lastError: unknown;
    let fetchResult: FetchResult | undefined;

    for (let attempt = 1; attempt <= attempts; attempt += 1) {
      try {
        fetchResult = await this.adapter.fetchReleasePage(cursor);
        break;
      } catch (error) {
        lastError = error;
      }
    }

    if (!fetchResult) {
      throw lastError ?? new RetryableFetchError("sync failed without a fetch result");
    }

    const rawCapture = await archiveRawCapture(this.archiveRoot, cursor, fetchResult);
    const payload = await parseArchivedReleasePayload(rawCapture);
    const records = normalizeReleaseRecords(rawCapture, payload);
    const nextCursor = fetchResult.nextPage
      ? {
          owner: cursor.owner,
          repo: cursor.repo,
          page: fetchResult.nextPage,
          etag: fetchResult.checkpointToken,
          maxAttempts: cursor.maxAttempts,
        }
      : undefined;

    return { rawCapture, records, nextCursor };
  }

  async replayFromArchive(rawCapture: RawCapture): Promise<NormalizedReleaseRecord[]> {
    const payload = await parseArchivedReleasePayload(rawCapture);
    return normalizeReleaseRecords(rawCapture, payload);
  }
}

type SyncRequest = {
  page?: number;
  etag?: string;
  maxAttempts?: number;
};

export const syncRouter = new Hono();

syncRouter.post("/sources/github-releases/:owner/:repo/sync", async (context) => {
  const body = await context.req.json<SyncRequest>();
  const service = new GitHubReleaseSyncService(new GitHubReleaseAdapter(), "./data/raw");
  const result = await service.syncReleasePage({
    owner: context.req.param("owner"),
    repo: context.req.param("repo"),
    page: body.page ?? 1,
    etag: body.etag,
    maxAttempts: body.maxAttempts ?? 2,
  });

  return context.json(
    {
      sourceName: SOURCE_NAME,
      rawPath: result.rawCapture.rawPath,
      normalizedCount: result.records.length,
      checkpointToken: result.rawCapture.checkpointToken,
      nextPage: result.nextCursor?.page,
    },
    202,
  );
});

async function sha256Hex(body: Uint8Array): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", body as unknown as BufferSource);
  return [...new Uint8Array(digest)]
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}
