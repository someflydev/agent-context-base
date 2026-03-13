const std = @import("std");
const zap = @import("zap");

fn sendJson(r: zap.Request, payload: []const u8) void {
    r.setContentType(.JSON) catch return;
    r.sendBody(payload) catch return;
}

fn sendHtml(r: zap.Request, payload: []const u8) void {
    r.setContentTypeFromFilename("fragment.html") catch return;
    r.sendBody(payload) catch return;
}

fn reportPayload(tenant_id: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(
        buffer,
        "{{\"tenant_id\":\"{s}\",\"report_id\":\"daily-signups\",\"total_events\":42}}",
        .{tenant_id},
    );
}

fn chartPayload(metric: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(
        buffer,
        "{{\"metric\":\"{s}\",\"series\":[{{\"name\":\"{s}\",\"points\":[{{\"x\":\"2026-03-01\",\"y\":18}},{{\"x\":\"2026-03-02\",\"y\":24}},{{\"x\":\"2026-03-03\",\"y\":31}}]}}]}}",
        .{ metric, metric },
    );
}

fn reportFragment(tenant_id: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(
        buffer,
        "<section id=\"report-card-{s}\" class=\"report-card\" hx-swap-oob=\"true\"><header class=\"report-card__header\">Tenant {s}</header><strong class=\"report-card__value\">42</strong><span class=\"report-card__status\">updated just now</span></section>",
        .{ tenant_id, tenant_id },
    );
}

fn on_request(r: zap.Request) !void {
    if (r.methodAsEnum() != .GET) return;

    if (r.path) |the_path| {
        if (std.mem.eql(u8, the_path, "/healthz")) {
            sendJson(r, "{\"status\":\"ok\",\"service\":\"zig-zap-jetzig-example\"}");
            return;
        }

        const report_prefix = "/api/reports/";
        if (std.mem.startsWith(u8, the_path, report_prefix)) {
            const tenant_id = the_path[report_prefix.len..];
            var buf: [256]u8 = undefined;
            sendJson(r, try reportPayload(tenant_id, &buf));
            return;
        }

        const fragment_prefix = "/fragments/report-card/";
        if (std.mem.startsWith(u8, the_path, fragment_prefix)) {
            const tenant_id = the_path[fragment_prefix.len..];
            var buf: [512]u8 = undefined;
            sendHtml(r, try reportFragment(tenant_id, &buf));
            return;
        }

        const chart_prefix = "/data/chart/";
        if (std.mem.startsWith(u8, the_path, chart_prefix)) {
            const metric = the_path[chart_prefix.len..];
            var buf: [512]u8 = undefined;
            sendJson(r, try chartPayload(metric, &buf));
            return;
        }
    }

    sendJson(r, "{\"status\":\"not-found\"}");
}

pub fn main() !void {
    var listener = zap.HttpListener.init(.{
        .port = 3000,
        .on_request = on_request,
        .log = true,
    });
    try listener.listen();

    std.debug.print("Listening on 0.0.0.0:3000\n", .{});

    zap.start(.{
        .threads = 2,
        .workers = 1,
    });
}
