name := "canonical-faker-scala"
version := "0.1.0"
scalaVersion := "3.3.3"

libraryDependencies ++= Seq(
  "net.datafaker" % "datafaker" % "2.0.1",
  "com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.15.2",
  "org.scalatest" %% "scalatest" % "3.2.18" % Test
)
