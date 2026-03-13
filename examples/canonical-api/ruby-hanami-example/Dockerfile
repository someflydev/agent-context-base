FROM ruby:3.3-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libsqlite3-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY Gemfile ./
RUN bundle install

COPY app ./app
COPY lib ./lib
COPY config.ru ./

EXPOSE 3000

CMD ["bundle", "exec", "rackup", "--host", "0.0.0.0", "--port", "3000", "config.ru"]
