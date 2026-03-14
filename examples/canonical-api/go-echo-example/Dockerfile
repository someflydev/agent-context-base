FROM golang:1.24-bookworm AS build

WORKDIR /app

COPY go.mod go.sum .
RUN go mod download

COPY main.go .
RUN go build -o server .

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=build /app/server ./server

EXPOSE 8080

CMD ["./server"]
