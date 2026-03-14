FROM debian:bookworm-slim AS build

ARG ZIG_VERSION=0.15.1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git xz-utils build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN set -eu; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
      amd64) zig_arch="x86_64" ;; \
      arm64) zig_arch="aarch64" ;; \
      *) echo "unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    zig_archive="zig-${zig_arch}-linux-${ZIG_VERSION}.tar.xz"; \
    curl -fsSL "https://ziglang.org/download/${ZIG_VERSION}/${zig_archive}" -o /tmp/zig.tar.xz; \
    tar -xf /tmp/zig.tar.xz -C /opt; \
    ln -s "/opt/zig-${zig_arch}-linux-${ZIG_VERSION}/zig" /usr/local/bin/zig

COPY build.zig build.zig.zon main.zig ./

RUN zig fetch --save "git+https://github.com/zigzap/zap#v0.11.0"
RUN zig build -Doptimize=ReleaseSafe
RUN cp "$(find /app/.zig-cache -name libfacil.io.so | head -n1)" /app/libfacil.io.so

FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/zig-out/bin/zig-zap-jetzig-example ./server
COPY --from=build /app/libfacil.io.so /usr/local/lib/libfacil.io.so

ENV LD_LIBRARY_PATH=/usr/local/lib

EXPOSE 3000

CMD ["./server"]
