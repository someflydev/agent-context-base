FROM nimlang/nim:2.2.0 AS build

WORKDIR /app

RUN nimble install -y jester

COPY main.nim .
RUN nim c --mm:orc -o:server main.nim

FROM nimlang/nim:2.2.0

WORKDIR /app

COPY --from=build /app/server ./server

EXPOSE 5000

CMD ["./server"]
