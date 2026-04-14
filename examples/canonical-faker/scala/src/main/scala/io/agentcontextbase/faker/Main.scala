package io.agentcontextbase.faker

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import java.io.PrintWriter
import java.nio.file.{Files, Paths}

object Main {
  val mapper = new ObjectMapper()
  mapper.registerModule(DefaultScalaModule)

  def main(args: Array[String]): Unit = {
    var profileName = "smoke"
    var outputDir = "./output"
    var format = "jsonl"

    args.sliding(2, 2).toList.foreach {
      case Array("--profile", p) => profileName = p
      case Array("--output-dir", o) => outputDir = o
      case Array("--format", f) => format = f
      case _ => ()
    }

    val profile = Profile.fromName(profileName)
    println(s"Generating $profileName profile (seed: ${profile.seed})...")

    val dataset = Pipeline.generate(profile)
    
    Files.createDirectories(Paths.get(outputDir))

    if (format == "jsonl") {
      writeJsonl(dataset, outputDir)
    }

    println(mapper.writeValueAsString(dataset.report.get))
  }

  private def writeJsonl(dataset: Dataset, dir: String): Unit = {
    def write[T](filename: String, items: Seq[T]): Unit = {
      val p = Paths.get(dir, filename)
      val pw = new PrintWriter(p.toFile)
      try {
        items.foreach(item => pw.println(mapper.writeValueAsString(item)))
      } finally {
        pw.close()
      }
      println(s"Wrote $filename")
    }

    write("organizations.jsonl", dataset.organizations)
    write("users.jsonl", dataset.users)
    write("memberships.jsonl", dataset.memberships)
    write("projects.jsonl", dataset.projects)
    write("api_keys.jsonl", dataset.api_keys)
    write("invitations.jsonl", dataset.invitations)
    write("audit_events.jsonl", dataset.audit_events)
  }
}
