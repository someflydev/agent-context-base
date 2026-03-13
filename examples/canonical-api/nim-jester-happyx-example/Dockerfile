FROM nimlang/nim:alpine AS build

WORKDIR /app

RUN nimble install -y jester

COPY main.nim .
RUN nim c -d:release -o:server main.nim

FROM alpine:3.21

WORKDIR /app

COPY --from=build /app/server ./server

EXPOSE 5000

CMD ["./server"]
