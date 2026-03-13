FROM debian:bookworm-slim AS build

ARG ZIG_VERSION=0.15.1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git xz-utils build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://ziglang.org/download/${ZIG_VERSION}/zig-linux-x86_64-${ZIG_VERSION}.tar.xz" -o /tmp/zig.tar.xz \
    && tar -xf /tmp/zig.tar.xz -C /opt \
    && ln -s "/opt/zig-linux-x86_64-${ZIG_VERSION}/zig" /usr/local/bin/zig

COPY build.zig build.zig.zon main.zig ./

RUN zig fetch --save "git+https://github.com/zigzap/zap#v0.11.0"
RUN zig build -Doptimize=ReleaseSafe

FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/zig-out/bin/zig-zap-jetzig-example ./server

EXPOSE 3000

CMD ["./server"]
