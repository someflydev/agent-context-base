ThisBuild / scalaVersion := "3.3.3"

lazy val root = (project in file("."))
  .settings(
    name := "scala-tapir-http4s-zio-runtime",
    libraryDependencies ++= Seq(
      "dev.zio" %% "zio" % "2.1.17",
      "dev.zio" %% "zio-json" % "0.7.44",
      "dev.zio" %% "zio-interop-cats" % "23.1.0.3",
      "org.http4s" %% "http4s-dsl" % "0.23.30",
      "org.http4s" %% "http4s-ember-server" % "0.23.30",
      "com.softwaremill.sttp.tapir" %% "tapir-core" % "1.11.21",
      "com.softwaremill.sttp.tapir" %% "tapir-json-zio" % "1.11.21",
      "com.softwaremill.sttp.tapir" %% "tapir-http4s-server" % "1.11.21",
    ),
  )
