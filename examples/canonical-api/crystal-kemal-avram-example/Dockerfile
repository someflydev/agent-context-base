FROM crystallang/crystal:1.12.2

WORKDIR /app

COPY shard.yml ./shard.yml
RUN shards install

COPY src ./src

RUN crystal build --release src/app.cr -o server

EXPOSE 3000

ENV KEMAL_ENV=production
ENV PORT=3000

CMD ["./server"]
