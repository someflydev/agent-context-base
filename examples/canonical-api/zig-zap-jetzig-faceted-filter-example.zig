// zig-zap-jetzig-faceted-filter-example.zig
//
// Demonstrates the split include/exclude filter panel pattern with Zig + Jetzig.
// The filter panel HTML is rendered via a .zmpl template file.
// See zig-zap-jetzig-faceted-filter-panel-template.zmpl for the template.
//
// NOTE: Zig's type system and Jetzig's early-stage API mean this example uses
// simplified single-string filter state. A production implementation would use
// ArrayList([]const u8) per filter field and a proper query-string parser.
// Multi-value params (e.g., ?status_out=archived&status_out=paused) are limited
// in early Jetzig/Zap versions; parse from query string manually if needed.

const std = @import("std");
const jetzig = @import("jetzig");

// ---------------------------------------------------------------------------
// Dataset
// ---------------------------------------------------------------------------

const ReportRow = struct {
    report_id: []const u8,
    team:      []const u8,
    status:    []const u8,
    region:    []const u8,
    events:    u32,
};

const report_rows = [_]ReportRow{
    .{ .report_id = "daily-signups",     .team = "growth",   .status = "active",   .region = "us",   .events = 12 },
    .{ .report_id = "trial-conversions", .team = "growth",   .status = "active",   .region = "us",   .events = 7  },
    .{ .report_id = "api-latency",       .team = "platform", .status = "paused",   .region = "eu",   .events = 5  },
    .{ .report_id = "checkout-failures", .team = "growth",   .status = "active",   .region = "eu",   .events = 9  },
    .{ .report_id = "queue-depth",       .team = "platform", .status = "active",   .region = "apac", .events = 11 },
    .{ .report_id = "legacy-import",     .team = "platform", .status = "archived", .region = "us",   .events = 4  },
};

const team_options   = [_][]const u8{ "growth", "platform" };
const status_options = [_][]const u8{ "active", "paused", "archived" };
const region_options = [_][]const u8{ "us", "eu", "apac" };

const QuickExclude = struct { dim: []const u8, val: []const u8 };
const quick_excludes = [_]QuickExclude{
    .{ .dim = "status", .val = "archived" },
    .{ .dim = "status", .val = "paused"   },
};

// ---------------------------------------------------------------------------
// QueryState
// NOTE: Uses single string per field for simplicity.
// A production implementation uses [][]const u8 (slice of strings) per field.
// ---------------------------------------------------------------------------

const QueryState = struct {
    team_in:    []const u8 = "",
    team_out:   []const u8 = "",
    status_in:  []const u8 = "",
    status_out: []const u8 = "",
    region_in:  []const u8 = "",
    region_out: []const u8 = "",
    query:      []const u8 = "",
    sort:       []const u8 = "events_desc",
};

fn queryParam(request: *jetzig.Request, key: []const u8) []const u8 {
    return request.queryParam(key) orelse "";
}

fn normalizeSort(s: []const u8) []const u8 {
    if (std.mem.eql(u8, s, "events_desc") or
        std.mem.eql(u8, s, "events_asc")  or
        std.mem.eql(u8, s, "name_asc")) return s;
    return "events_desc";
}

fn buildQueryState(request: *jetzig.Request) QueryState {
    return .{
        .team_in    = queryParam(request, "team_in"),
        .team_out   = queryParam(request, "team_out"),
        .status_in  = queryParam(request, "status_in"),
        .status_out = queryParam(request, "status_out"),
        .region_in  = queryParam(request, "region_in"),
        .region_out = queryParam(request, "region_out"),
        .query      = queryParam(request, "query"),
        .sort       = normalizeSort(queryParam(request, "sort")),
    };
}

// ---------------------------------------------------------------------------
// Text search helper
// Zig string lowercasing requires allocator; this example uses a simplified
// approach — case-insensitive ASCII comparison without heap allocation.
// ---------------------------------------------------------------------------

fn asciiToLower(c: u8) u8 {
    if (c >= 'A' and c <= 'Z') return c + 32;
    return c;
}

fn containsIgnoreCase(haystack: []const u8, needle: []const u8) bool {
    if (needle.len == 0) return true;
    if (needle.len > haystack.len) return false;
    var i: usize = 0;
    while (i <= haystack.len - needle.len) : (i += 1) {
        var match = true;
        for (needle, 0..) |nc, j| {
            if (asciiToLower(haystack[i + j]) != asciiToLower(nc)) {
                match = false;
                break;
            }
        }
        if (match) return true;
    }
    return false;
}

fn applyTextSearch(
    allocator: std.mem.Allocator,
    rows: []const ReportRow,
    q: []const u8,
) ![]ReportRow {
    if (q.len == 0) {
        const buf = try allocator.alloc(ReportRow, rows.len);
        @memcpy(buf, rows);
        return buf;
    }
    var list = std.ArrayList(ReportRow).init(allocator);
    for (rows) |row| {
        if (containsIgnoreCase(row.report_id, q)) {
            try list.append(row);
        }
    }
    return list.toOwnedSlice();
}

// ---------------------------------------------------------------------------
// Sort helper
// ---------------------------------------------------------------------------

fn compareRows(sort_val: []const u8, a: ReportRow, b: ReportRow) bool {
    if (std.mem.eql(u8, sort_val, "events_asc")) {
        if (a.events != b.events) return a.events < b.events;
        return std.mem.lessThan(u8, a.report_id, b.report_id);
    } else if (std.mem.eql(u8, sort_val, "name_asc")) {
        return std.mem.lessThan(u8, a.report_id, b.report_id);
    } else { // events_desc
        if (a.events != b.events) return a.events > b.events;
        return std.mem.lessThan(u8, a.report_id, b.report_id);
    }
}

const SortContext = struct {
    sort_val: []const u8,
    pub fn lessThan(ctx: SortContext, a: ReportRow, b: ReportRow) bool {
        return compareRows(ctx.sort_val, a, b);
    }
};

fn sortRows(
    allocator: std.mem.Allocator,
    rows: []const ReportRow,
    sort_val: []const u8,
) ![]ReportRow {
    const buf = try allocator.alloc(ReportRow, rows.len);
    @memcpy(buf, rows);
    std.sort.block(ReportRow, buf, SortContext{ .sort_val = sort_val }, SortContext.lessThan);
    return buf;
}

// ---------------------------------------------------------------------------
// Filter helpers (comptime-compatible)
// ---------------------------------------------------------------------------

fn matchesDimSingle(value: []const u8, include_val: []const u8, exclude_val: []const u8) bool {
    // Single-value include/exclude check
    if (include_val.len > 0 and !std.mem.eql(u8, value, include_val)) return false;
    if (exclude_val.len > 0 and std.mem.eql(u8, value, exclude_val)) return false;
    return true;
}

fn countFilteredRows(allocator: std.mem.Allocator, state: QueryState) !usize {
    const searched = try applyTextSearch(allocator, &report_rows, state.query);
    defer allocator.free(searched);
    var count: usize = 0;
    for (searched) |row| {
        if (matchesDimSingle(row.team,   state.team_in,   state.team_out)   and
            matchesDimSingle(row.status, state.status_in, state.status_out) and
            matchesDimSingle(row.region, state.region_in, state.region_out)) {
            count += 1;
        }
    }
    return count;
}

fn countFacet(allocator: std.mem.Allocator, state: QueryState, comptime dim: []const u8, option: []const u8) !usize {
    const searched = try applyTextSearch(allocator, &report_rows, state.query);
    defer allocator.free(searched);
    var count: usize = 0;
    for (searched) |row| {
        const val = @field(row, dim);
        // Apply all OTHER dimensions fully; relax THIS dim's include; still apply THIS dim's exclude
        const other_pass = if (std.mem.eql(u8, dim, "team"))
            matchesDimSingle(row.status, state.status_in, state.status_out) and
            matchesDimSingle(row.region, state.region_in, state.region_out) and
            (state.team_out.len == 0 or !std.mem.eql(u8, row.team, state.team_out))
        else if (std.mem.eql(u8, dim, "status"))
            matchesDimSingle(row.team,   state.team_in,   state.team_out)   and
            matchesDimSingle(row.region, state.region_in, state.region_out) and
            (state.status_out.len == 0 or !std.mem.eql(u8, row.status, state.status_out))
        else
            matchesDimSingle(row.team,   state.team_in,   state.team_out)   and
            matchesDimSingle(row.status, state.status_in, state.status_out) and
            (state.region_out.len == 0 or !std.mem.eql(u8, row.region, state.region_out));
        if (other_pass and std.mem.eql(u8, val, option)) count += 1;
    }
    return count;
}

fn countExcludeImpact(allocator: std.mem.Allocator, state: QueryState, comptime dim: []const u8, option: []const u8) !usize {
    // Count rows that would be removed by excluding this option
    // Apply all OTHER dims fully; apply THIS dim's other excludes (none in single-value model); no D_in
    const searched = try applyTextSearch(allocator, &report_rows, state.query);
    defer allocator.free(searched);
    var count: usize = 0;
    for (searched) |row| {
        const val = @field(row, dim);
        const other_pass = if (std.mem.eql(u8, dim, "team"))
            matchesDimSingle(row.status, state.status_in, state.status_out) and
            matchesDimSingle(row.region, state.region_in, state.region_out)
        else if (std.mem.eql(u8, dim, "status"))
            matchesDimSingle(row.team,   state.team_in,   state.team_out) and
            matchesDimSingle(row.region, state.region_in, state.region_out)
        else
            matchesDimSingle(row.team,   state.team_in,   state.team_out) and
            matchesDimSingle(row.status, state.status_in, state.status_out);
        if (other_pass and std.mem.eql(u8, val, option)) count += 1;
    }
    return count;
}

// ---------------------------------------------------------------------------
// Route handlers
// ---------------------------------------------------------------------------

// GET /ui/reports — Full dashboard page
pub fn index(request: *jetzig.Request) !jetzig.View {
    const allocator = request.allocator;
    const state = buildQueryState(request);
    var data = try request.data(.object);

    // Pass filter state and counts to the template
    try data.put("team_in",    state.team_in);
    try data.put("team_out",   state.team_out);
    try data.put("status_in",  state.status_in);
    try data.put("status_out", state.status_out);
    try data.put("region_in",  state.region_in);
    try data.put("region_out", state.region_out);
    try data.put("query",      state.query);
    try data.put("sort",       state.sort);

    // Pass result count
    const n = try countFilteredRows(allocator, state);
    try data.put("result_count", n);

    // Pass exclude impact counts for quick excludes
    try data.put("archived_impact", try countExcludeImpact(allocator, state, "status", "archived"));
    try data.put("paused_impact",   try countExcludeImpact(allocator, state, "status", "paused"));
    try data.put("archived_active", std.mem.eql(u8, state.status_out, "archived"));
    try data.put("paused_active",   std.mem.eql(u8, state.status_out, "paused"));

    // Pass sort select state
    try data.put("sort_events_desc_selected", std.mem.eql(u8, state.sort, "events_desc"));
    try data.put("sort_events_asc_selected",  std.mem.eql(u8, state.sort, "events_asc"));
    try data.put("sort_name_asc_selected",    std.mem.eql(u8, state.sort, "name_asc"));

    // Pass sorted rows for results
    const searched = try applyTextSearch(allocator, &report_rows, state.query);
    defer allocator.free(searched);
    var filtered_list = std.ArrayList(ReportRow).init(allocator);
    defer filtered_list.deinit();
    for (searched) |row| {
        if (matchesDimSingle(row.team,   state.team_in,   state.team_out)   and
            matchesDimSingle(row.status, state.status_in, state.status_out) and
            matchesDimSingle(row.region, state.region_in, state.region_out)) {
            try filtered_list.append(row);
        }
    }
    const sorted = try sortRows(allocator, filtered_list.items, state.sort);
    defer allocator.free(sorted);
    var rows_arr = try data.array();
    for (sorted) |row| {
        var obj = try data.object();
        try obj.put("report_id", row.report_id);
        try obj.put("team",      row.team);
        try obj.put("status",    row.status);
        try obj.put("region",    row.region);
        try obj.put("events",    row.events);
        try rows_arr.append(obj);
    }
    try data.put("rows", rows_arr);

    request.response.content_type = "text/html";
    return request.renderTemplate("reports/filter_panel", .ok);
}

// GET /ui/reports/results — HTMX partial: result count badge + results list
pub fn results(request: *jetzig.Request) !jetzig.View {
    const allocator = request.allocator;
    const state = buildQueryState(request);
    var data = try request.data(.object);

    const n = try countFilteredRows(allocator, state);
    try data.put("result_count", n);
    try data.put("status_out",   state.status_out);
    try data.put("query",        state.query);
    try data.put("sort",         state.sort);

    try data.put("sort_events_desc_selected", std.mem.eql(u8, state.sort, "events_desc"));
    try data.put("sort_events_asc_selected",  std.mem.eql(u8, state.sort, "events_asc"));
    try data.put("sort_name_asc_selected",    std.mem.eql(u8, state.sort, "name_asc"));

    const searched = try applyTextSearch(allocator, &report_rows, state.query);
    defer allocator.free(searched);
    var filtered_list = std.ArrayList(ReportRow).init(allocator);
    defer filtered_list.deinit();
    for (searched) |row| {
        if (matchesDimSingle(row.team,   state.team_in,   state.team_out)   and
            matchesDimSingle(row.status, state.status_in, state.status_out) and
            matchesDimSingle(row.region, state.region_in, state.region_out)) {
            try filtered_list.append(row);
        }
    }
    const sorted = try sortRows(allocator, filtered_list.items, state.sort);
    defer allocator.free(sorted);
    var rows_arr = try data.array();
    for (sorted) |row| {
        var obj = try data.object();
        try obj.put("report_id", row.report_id);
        try obj.put("team",      row.team);
        try obj.put("status",    row.status);
        try obj.put("region",    row.region);
        try rows_arr.append(obj);
    }
    try data.put("rows", rows_arr);

    request.response.content_type = "text/html";
    return request.renderTemplate("reports/results_fragment", .ok);
}

// GET /ui/reports/filter-panel — HTMX partial: filter panel only
pub fn filterPanel(request: *jetzig.Request) !jetzig.View {
    const allocator = request.allocator;
    const state = buildQueryState(request);
    var data = try request.data(.object);

    try data.put("team_in",    state.team_in);
    try data.put("team_out",   state.team_out);
    try data.put("status_in",  state.status_in);
    try data.put("status_out", state.status_out);
    try data.put("region_in",  state.region_in);
    try data.put("region_out", state.region_out);
    try data.put("query",      state.query);
    try data.put("sort",       state.sort);
    try data.put("archived_impact", try countExcludeImpact(allocator, state, "status", "archived"));
    try data.put("paused_impact",   try countExcludeImpact(allocator, state, "status", "paused"));
    try data.put("archived_active", std.mem.eql(u8, state.status_out, "archived"));
    try data.put("paused_active",   std.mem.eql(u8, state.status_out, "paused"));

    request.response.content_type = "text/html";
    return request.renderTemplate("reports/filter_panel_partial", .ok);
}

// GET /healthz
pub fn healthz(request: *jetzig.Request) !jetzig.View {
    var data = try request.data(.object);
    try data.put("status", "ok");
    return request.render(.ok);
}
