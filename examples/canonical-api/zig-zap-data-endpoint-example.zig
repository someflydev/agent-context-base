const std = @import("std");
const zap = @import("zap");

fn buildSeriesPayload(metric: []const u8, buffer: []u8) ![]const u8 {
    return std.fmt.bufPrint(
        buffer,
        "{{\"metric\":\"{s}\",\"series\":[{{\"name\":\"{s}\",\"points\":[{{\"x\":\"2026-03-01\",\"y\":18}},{{\"x\":\"2026-03-02\",\"y\":24}},{{\"x\":\"2026-03-03\",\"y\":31}}]}}]}}",
        .{ metric, metric },
    );
}

fn on_request(r: zap.Request) !void {
    if (r.methodAsEnum() != .GET) return;

    if (r.path) |the_path| {
        const prefix = "/data/series/";
        if (!std.mem.startsWith(u8, the_path, prefix)) return;

        const metric = the_path[prefix.len..];
        var buf: [512]u8 = undefined;
        const payload = try buildSeriesPayload(metric, &buf);

        r.setContentType(.JSON) catch return;
        r.sendBody(payload) catch return;
    }
}
