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

    args.sliding(2, 2).toList.collect {
      case Array("--profile", p) => profileName = p
      case Array("--output", o) => outputDir = o
      case Array("--format", f) => format = f
    }

    val profile = Profile.fromName(profileName)
    println(s"Generating $profileName profile (seed: ${profile.seed})...")

    val dataset = Pipeline.generate(profile)
    
    Files.createDirectories(Paths.get(outputDir))

    if (format == "jsonl") {
      writeJsonl(dataset, outputDir, profileName)
    }

    println(mapper.writeValueAsString(dataset.report.get))
  }

  private def writeJsonl(dataset: Dataset, dir: String, profileName: String): Unit = {
    val p = Paths.get(dir, s"tenant_core_$${profileName}.jsonl")
    val pw = new PrintWriter(p.toFile)
    try {
      dataset.organizations.foreach(o => pw.println(mapper.writeValueAsString(Map("type" -> "organization", "data" -> o))))
      dataset.users.foreach(u => pw.println(mapper.writeValueAsString(Map("type" -> "user", "data" -> u))))
      dataset.memberships.foreach(m => pw.println(mapper.writeValueAsString(Map("type" -> "membership", "data" -> m))))
      dataset.projects.foreach(p => pw.println(mapper.writeValueAsString(Map("type" -> "project", "data" -> p))))
      dataset.api_keys.foreach(a => pw.println(mapper.writeValueAsString(Map("type" -> "api_key", "data" -> a))))
      dataset.invitations.foreach(i => pw.println(mapper.writeValueAsString(Map("type" -> "invitation", "data" -> i))))
      dataset.audit_events.foreach(a => pw.println(mapper.writeValueAsString(Map("type" -> "audit_event", "data" -> a))))
    } finally {
      pw.close()
    }
    println(s"Wrote dataset to $p")
  }
}
