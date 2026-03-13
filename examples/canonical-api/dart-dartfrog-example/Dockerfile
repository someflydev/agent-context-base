FROM dart:stable

WORKDIR /app

RUN dart pub global activate dart_frog_cli

COPY pubspec.yaml ./
RUN dart pub get

COPY routes routes
RUN dart_frog build

ENV PATH="/root/.pub-cache/bin:${PATH}"

EXPOSE 8080

CMD ["dart", "build/bin/server.dart"]
