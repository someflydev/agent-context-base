const std = @import("std");
const zap = @import("zap");

const SOURCE_NAME = "github-releases";
const ADAPTER_VERSION = "github-releases-v1";

const SyncCursor = struct {
    owner: []const u8,
    repo: []const u8,
    page: usize = 1,
    etag: ?[]const u8 = null,
    max_attempts: u8 = 2,

    pub fn checkpointToken(self: @This(), buffer: []u8) ![]const u8 {
        if (self.etag) |etag| return etag;
        return std.fmt.bufPrint(buffer, "page={d}", .{@max(self.page, 1)});
    }
};

const FetchResult = struct {
    body: []u8,
    fetched_at: i64,
    status_code: u16,
    content_type: []const u8,
    request_url: []const u8,
    checkpoint_token: []const u8,
    next_page: ?usize,
};

const RawCapture = struct {
    source_name: []const u8,
    owner: []const u8,
    repo: []const u8,
    fetched_at: []const u8,
    raw_path: []const u8,
    metadata_path: []const u8,
    sha256: []const u8,
    checkpoint_token: []const u8,
    request_url: []const u8,
};

const ReleaseProvenance = struct {
    source_name: []const u8,
    raw_path: []const u8,
    fetched_at: []const u8,
    sha256: []const u8,
    checkpoint_token: []const u8,
    adapter_version: []const u8,
};

const CanonicalReleaseRecord = struct {
    canonical_id: []const u8,
    source_id: i64,
    owner: []const u8,
    repo: []const u8,
    external_slug: []const u8,
    title: []const u8,
    published_at: []const u8,
    canonical_url: []const u8,
    provenance: ReleaseProvenance,
};

const SyncResult = struct {
    raw_capture: RawCapture,
    records: []CanonicalReleaseRecord,
    next_cursor: ?SyncCursor,
};

const SyncReceipt = struct {
    source_name: []const u8,
    raw_path: []const u8,
    normalized_count: usize,
    checkpoint_token: []const u8,
    next_page: ?usize,
};

const GitHubReleasePayload = struct {
    id: i64,
    tag_name: []const u8,
    name: ?[]const u8 = null,
    html_url: []const u8,
    published_at: ?[]const u8 = null,
    draft: bool = false,
};

const GitHubReleaseAdapter = struct {
    allocator: std.mem.Allocator,
    client: std.http.Client,

    pub fn fetchReleasePage(self: *GitHubReleaseAdapter, cursor: SyncCursor) !FetchResult {
        const page = @max(cursor.page, 1);
        const request_url = try std.fmt.allocPrint(
            self.allocator,
            "https://api.github.com/repos/{s}/{s}/releases?per_page=50&page={d}",
            .{ cursor.owner, cursor.repo, page },
        );

        var checkpoint_buffer: [32]u8 = undefined;
        const fallback_checkpoint = try cursor.checkpointToken(&checkpoint_buffer);

        var headers = std.ArrayList(std.http.Header).init(self.allocator);
        defer headers.deinit();
        try headers.append(.{ .name = "accept", .value = "application/vnd.github+json" });
        try headers.append(.{ .name = "user-agent", .value = "agent-context-base-canonical-example" });
        try headers.append(.{ .name = "x-github-api-version", .value = "2022-11-28" });
        if (cursor.etag) |etag| {
            try headers.append(.{ .name = "if-none-match", .value = etag });
        }

        var request = try self.client.open(.GET, try std.Uri.parse(request_url), .{
            .extra_headers = headers.items,
        });
        defer request.deinit();

        try request.send();
        try request.finish();
        try request.wait();

        if (request.response.status == .too_many_requests or request.response.status.class() == .server_error) {
            return error.RetryableFetch;
        }

        var body = std.ArrayList(u8).init(self.allocator);
        defer body.deinit();
        try request.reader().readAllArrayList(&body, 1024 * 256);

        const raw_body = try body.toOwnedSlice();
        const checkpoint = request.response.headers.getFirstValue("etag") orelse fallback_checkpoint;

        return FetchResult{
            .body = raw_body,
            .fetched_at = std.time.timestamp(),
            .status_code = @intFromEnum(request.response.status),
            .content_type = try self.allocator.dupe(
                u8,
                request.response.headers.getFirstValue("content-type") orelse "application/json",
            ),
            .request_url = request_url,
            .checkpoint_token = try self.allocator.dupe(u8, checkpoint),
            .next_page = if (raw_body.len == 0) null else page + 1,
        };
    }
};

fn archiveRawCapture(
    allocator: std.mem.Allocator,
    archive_root: []const u8,
    cursor: SyncCursor,
    fetch_result: FetchResult,
) !RawCapture {
    var stamp_buffer: [32]u8 = undefined;
    const stamp = try std.fmt.bufPrint(&stamp_buffer, "{d}", .{fetch_result.fetched_at});
    const capture_dir = try std.fs.path.join(allocator, &.{ archive_root, SOURCE_NAME, cursor.owner, cursor.repo, stamp });
    try std.fs.cwd().makePath(capture_dir);

    const page = @max(cursor.page, 1);
    const raw_path = try std.fmt.allocPrint(allocator, "{s}/page-{d}.json", .{ capture_dir, page });
    const metadata_path = try std.fmt.allocPrint(allocator, "{s}/page-{d}.metadata.json", .{ capture_dir, page });

    {
        var raw_file = try std.fs.cwd().createFile(raw_path, .{ .truncate = true });
        defer raw_file.close();
        try raw_file.writeAll(fetch_result.body);
    }

    const digest = std.crypto.hash.sha2.Sha256.hash(fetch_result.body, .{});
    const sha256 = try std.fmt.allocPrint(allocator, "{x}", .{digest});
    const fetched_at = try std.fmt.allocPrint(allocator, "{d}", .{fetch_result.fetched_at});

    const capture = RawCapture{
        .source_name = SOURCE_NAME,
        .owner = try allocator.dupe(u8, cursor.owner),
        .repo = try allocator.dupe(u8, cursor.repo),
        .fetched_at = fetched_at,
        .raw_path = raw_path,
        .metadata_path = metadata_path,
        .sha256 = sha256,
        .checkpoint_token = try allocator.dupe(u8, fetch_result.checkpoint_token),
        .request_url = try allocator.dupe(u8, fetch_result.request_url),
    };

    const metadata_json = try std.fmt.allocPrint(
        allocator,
        "{{\"sourceName\":\"{s}\",\"owner\":\"{s}\",\"repo\":\"{s}\",\"fetchedAt\":\"{s}\",\"rawPath\":\"{s}\",\"metadataPath\":\"{s}\",\"sha256\":\"{s}\",\"checkpointToken\":\"{s}\",\"requestUrl\":\"{s}\"}}",
        .{
            capture.source_name,
            capture.owner,
            capture.repo,
            capture.fetched_at,
            capture.raw_path,
            capture.metadata_path,
            capture.sha256,
            capture.checkpoint_token,
            capture.request_url,
        },
    );

    {
        var metadata_file = try std.fs.cwd().createFile(metadata_path, .{ .truncate = true });
        defer metadata_file.close();
        try metadata_file.writeAll(metadata_json);
    }

    return capture;
}

fn parseArchivedReleasePayload(
    allocator: std.mem.Allocator,
    raw_capture: RawCapture,
) !std.json.Parsed([]GitHubReleasePayload) {
    const raw_bytes = try std.fs.cwd().readFileAlloc(allocator, raw_capture.raw_path, 1024 * 1024);
    defer allocator.free(raw_bytes);

    return try std.json.parseFromSlice([]GitHubReleasePayload, allocator, raw_bytes, .{
        .allocate = .alloc_always,
    });
}

fn normalizeReleaseRecords(
    allocator: std.mem.Allocator,
    raw_capture: RawCapture,
    payload: []GitHubReleasePayload,
) ![]CanonicalReleaseRecord {
    var records = std.ArrayList(CanonicalReleaseRecord).init(allocator);
    defer records.deinit();

    const provenance = ReleaseProvenance{
        .source_name = raw_capture.source_name,
        .raw_path = raw_capture.raw_path,
        .fetched_at = raw_capture.fetched_at,
        .sha256 = raw_capture.sha256,
        .checkpoint_token = raw_capture.checkpoint_token,
        .adapter_version = ADAPTER_VERSION,
    };

    for (payload) |item| {
        if (item.draft) continue;
        const external_slug = item.tag_name;
        const title = item.name orelse external_slug;
        try records.append(.{
            .canonical_id = try std.fmt.allocPrint(
                allocator,
                "{s}:{s}/{s}:{d}",
                .{ SOURCE_NAME, raw_capture.owner, raw_capture.repo, item.id },
            ),
            .source_id = item.id,
            .owner = try allocator.dupe(u8, raw_capture.owner),
            .repo = try allocator.dupe(u8, raw_capture.repo),
            .external_slug = try allocator.dupe(u8, external_slug),
            .title = try allocator.dupe(u8, title),
            .published_at = try allocator.dupe(u8, item.published_at orelse ""),
            .canonical_url = try allocator.dupe(u8, item.html_url),
            .provenance = provenance,
        });
    }

    return try records.toOwnedSlice();
}

const GitHubReleaseSyncService = struct {
    allocator: std.mem.Allocator,
    archive_root: []const u8,
    adapter: *GitHubReleaseAdapter,

    pub fn syncReleasePage(self: *GitHubReleaseSyncService, cursor: SyncCursor) !SyncResult {
        const attempts = @max(cursor.max_attempts, 1);
        var fetch_result: ?FetchResult = null;
        var attempt: u8 = 0;

        while (attempt < attempts) : (attempt += 1) {
            fetch_result = self.adapter.fetchReleasePage(cursor) catch |err| switch (err) {
                error.RetryableFetch => null,
                else => return err,
            };
            if (fetch_result != null) break;
        }

        const resolved_fetch = fetch_result orelse return error.RetryableFetch;
        const raw_capture = try archiveRawCapture(self.allocator, self.archive_root, cursor, resolved_fetch);
        var payload = try parseArchivedReleasePayload(self.allocator, raw_capture);
        defer payload.deinit();

        const records = try normalizeReleaseRecords(self.allocator, raw_capture, payload.value);
        const next_cursor = if (resolved_fetch.next_page) |next_page|
            SyncCursor{
                .owner = cursor.owner,
                .repo = cursor.repo,
                .page = next_page,
                .etag = resolved_fetch.checkpoint_token,
                .max_attempts = cursor.max_attempts,
            }
        else
            null;

        return SyncResult{
            .raw_capture = raw_capture,
            .records = records,
            .next_cursor = next_cursor,
        };
    }

    pub fn replayFromArchive(self: *GitHubReleaseSyncService, raw_capture: RawCapture) ![]CanonicalReleaseRecord {
        var payload = try parseArchivedReleasePayload(self.allocator, raw_capture);
        defer payload.deinit();
        return try normalizeReleaseRecords(self.allocator, raw_capture, payload.value);
    }
};

fn on_request(r: zap.Request) !void {
    if (r.methodAsEnum() != .POST) return;

    if (r.path) |the_path| {
        const prefix = "/sources/github-releases/";
        if (!std.mem.startsWith(u8, the_path, prefix)) return;

        const tail = the_path[prefix.len..];
        var segments = std.mem.splitScalar(u8, tail, '/');
        const owner = segments.next() orelse return;
        const repo = segments.next() orelse return;
        const action = segments.next() orelse return;
        if (!std.mem.eql(u8, action, "sync")) return;

        var gpa = std.heap.GeneralPurposeAllocator(.{}){};
        defer _ = gpa.deinit();
        const allocator = gpa.allocator();

        var adapter = GitHubReleaseAdapter{
            .allocator = allocator,
            .client = .{ .allocator = allocator },
        };
        defer adapter.client.deinit();

        var service = GitHubReleaseSyncService{
            .allocator = allocator,
            .archive_root = "./data/raw",
            .adapter = &adapter,
        };

        const result = try service.syncReleasePage(.{
            .owner = owner,
            .repo = repo,
            .page = 1,
            .max_attempts = 2,
        });

        const receipt = SyncReceipt{
            .source_name = SOURCE_NAME,
            .raw_path = result.raw_capture.raw_path,
            .normalized_count = result.records.len,
            .checkpoint_token = result.raw_capture.checkpoint_token,
            .next_page = if (result.next_cursor) |next_cursor| next_cursor.page else null,
        };

        var buffer: [1024]u8 = undefined;
        const payload = try std.fmt.bufPrint(
            &buffer,
            "{{\"sourceName\":\"{s}\",\"rawPath\":\"{s}\",\"normalizedCount\":{d},\"checkpointToken\":\"{s}\",\"nextPage\":{d}}}",
            .{
                receipt.source_name,
                receipt.raw_path,
                receipt.normalized_count,
                receipt.checkpoint_token,
                receipt.next_page orelse 0,
            },
        );

        r.setContentType(.JSON) catch return;
        r.sendBody(payload) catch return;
    }
}
