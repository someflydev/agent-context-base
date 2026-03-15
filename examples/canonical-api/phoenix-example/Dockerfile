FROM elixir:1.17-alpine

ENV MIX_ENV=dev
ENV PORT=4000

WORKDIR /app

RUN mix local.hex --force && mix local.rebar --force

COPY mix.exs .
RUN mix deps.get

COPY config ./config
COPY lib ./lib

EXPOSE 4000
CMD ["mix", "phx.server"]
