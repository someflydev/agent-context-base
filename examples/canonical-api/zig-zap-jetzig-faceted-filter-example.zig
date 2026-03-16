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
};

fn queryParam(request: *jetzig.Request, key: []const u8) []const u8 {
    return request.queryParam(key) orelse "";
}

fn buildQueryState(request: *jetzig.Request) QueryState {
    return .{
        .team_in    = queryParam(request, "team_in"),
        .team_out   = queryParam(request, "team_out"),
        .status_in  = queryParam(request, "status_in"),
        .status_out = queryParam(request, "status_out"),
        .region_in  = queryParam(request, "region_in"),
        .region_out = queryParam(request, "region_out"),
    };
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

fn countFilteredRows(state: QueryState) usize {
    var count: usize = 0;
    for (report_rows) |row| {
        if (matchesDimSingle(row.team,   state.team_in,   state.team_out)   and
            matchesDimSingle(row.status, state.status_in, state.status_out) and
            matchesDimSingle(row.region, state.region_in, state.region_out)) {
            count += 1;
        }
    }
    return count;
}

fn countFacet(state: QueryState, comptime dim: []const u8, option: []const u8) usize {
    var count: usize = 0;
    for (report_rows) |row| {
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

fn countExcludeImpact(state: QueryState, comptime dim: []const u8, option: []const u8) usize {
    // Count rows that would be removed by excluding this option
    // Apply all OTHER dims fully; apply THIS dim's other excludes (none in single-value model); no D_in
    var count: usize = 0;
    for (report_rows) |row| {
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
    const state = buildQueryState(request);
    var data = try request.data(.object);

    // Pass filter state and counts to the template
    try data.put("team_in",    state.team_in);
    try data.put("team_out",   state.team_out);
    try data.put("status_in",  state.status_in);
    try data.put("status_out", state.status_out);
    try data.put("region_in",  state.region_in);
    try data.put("region_out", state.region_out);

    // Pass result count
    const n = countFilteredRows(state);
    try data.put("result_count", n);

    // Pass exclude impact counts for quick excludes
    try data.put("archived_impact", countExcludeImpact(state, "status", "archived"));
    try data.put("paused_impact",   countExcludeImpact(state, "status", "paused"));
    try data.put("archived_active", std.mem.eql(u8, state.status_out, "archived"));
    try data.put("paused_active",   std.mem.eql(u8, state.status_out, "paused"));

    request.response.content_type = "text/html";
    return request.renderTemplate("reports/filter_panel", .ok);
}

// GET /ui/reports/results — HTMX partial: result count badge + results list
pub fn results(request: *jetzig.Request) !jetzig.View {
    const state = buildQueryState(request);
    var data = try request.data(.object);

    const n = countFilteredRows(state);
    try data.put("result_count", n);
    try data.put("status_out", state.status_out);

    request.response.content_type = "text/html";
    return request.renderTemplate("reports/results_fragment", .ok);
}

// GET /ui/reports/filter-panel — HTMX partial: filter panel only
pub fn filterPanel(request: *jetzig.Request) !jetzig.View {
    const state = buildQueryState(request);
    var data = try request.data(.object);

    try data.put("team_in",    state.team_in);
    try data.put("team_out",   state.team_out);
    try data.put("status_in",  state.status_in);
    try data.put("status_out", state.status_out);
    try data.put("region_in",  state.region_in);
    try data.put("region_out", state.region_out);
    try data.put("archived_impact", countExcludeImpact(state, "status", "archived"));
    try data.put("paused_impact",   countExcludeImpact(state, "status", "paused"));
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
