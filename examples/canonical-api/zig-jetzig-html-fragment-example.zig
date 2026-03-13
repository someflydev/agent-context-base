const std = @import("std");
const jetzig = @import("jetzig");

// Equivalent to src/app/views/reports/summary_fragment.zig in a Jetzig app.
pub fn index(request: *jetzig.Request) !jetzig.View {
    request.response.content_type = "text/html";
    return request.renderTemplate("reports/summary_fragment", .ok);
}

test "fragment endpoint renders htmx-friendly summary" {
    var app = try jetzig.testing.app(std.testing.allocator, @import("routes"));
    defer app.deinit();

    const response = try app.request(.GET, "/reports/summary_fragment", .{});
    try response.expectStatus(.ok);
    try response.expectBodyContains("hx-swap-oob");
}
