FROM rust:1.87-bookworm AS build

WORKDIR /app

COPY Cargo.toml .
COPY src ./src

RUN cargo build --release

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=build /app/target/release/rust-axum-runtime ./server

EXPOSE 3000

CMD ["./server"]
