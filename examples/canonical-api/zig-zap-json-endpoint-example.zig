const std = @import("std");
const zap = @import("zap");

const HealthSnapshot = struct {
    service: []const u8,
    status: []const u8,
};

fn on_request(r: zap.Request) !void {
    if (r.methodAsEnum() != .GET) return;

    if (r.path) |the_path| {
        if (!std.mem.eql(u8, the_path, "/api/health")) return;

        const snapshot = HealthSnapshot{
            .service = "zig-zap-jetzig",
            .status = "ok",
        };

        var buf: [128]u8 = undefined;
        const payload = try std.fmt.bufPrint(
            &buf,
            "{{\"service\":\"{s}\",\"status\":\"{s}\"}}",
            .{ snapshot.service, snapshot.status },
        );

        r.setContentType(.JSON) catch return;
        r.sendBody(payload) catch return;
    }
}
