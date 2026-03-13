FROM gradle:8.10.2-jdk21 AS build

WORKDIR /app

COPY settings.gradle.kts build.gradle.kts ./
RUN gradle --no-daemon dependencies > /tmp/gradle-dependencies.log

COPY src ./src
RUN gradle --no-daemon installDist

FROM eclipse-temurin:21-jre-jammy

WORKDIR /app

COPY --from=build /app/build/install/kotlin-http4k-exposed-example ./

EXPOSE 8080

CMD ["bin/kotlin-http4k-exposed-example"]
