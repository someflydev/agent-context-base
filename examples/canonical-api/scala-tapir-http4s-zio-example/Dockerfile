FROM sbtscala/scala-sbt:eclipse-temurin-21.0.8_9_1.11.7_3.7.3

WORKDIR /app

COPY build.sbt ./
COPY project ./project
RUN sbt update

COPY src ./src

EXPOSE 8080

CMD ["sbt", "run"]
