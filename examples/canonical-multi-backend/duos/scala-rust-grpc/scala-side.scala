// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// scala-side.scala — Scala Akka Streams pipeline that delegates per-element
// hot-path compute to a Rust tonic gRPC server (rust-side.rs) via mapAsync.
//
// This is the central Akka Streams integration pattern from duo-scala-rust.md:
// Scala orchestrates the streaming topology; Rust handles the compute kernel.
//
// build.sbt dependencies:
//   "com.typesafe.akka" %% "akka-stream"       % "2.8.5"
//   "com.typesafe.akka" %% "akka-actor-typed"  % "2.8.5"
//   "com.typesafe.akka" %% "akka-http"         % "10.5.3"   // for /healthz
//   // sbt-akka-grpc plugin generates KernelServiceClient from service.proto
//   // addSbtPlugin("com.lightbend.akka.grpc" % "sbt-akka-grpc" % "2.4.0")
//
// Stub generation:
//   sbt-akka-grpc generates the KernelServiceClient during sbt compile.
//   Place service.proto in src/main/protobuf/. The plugin generates:
//     kernel.v1.KernelServiceClient        (Akka gRPC async client)
//     kernel.v1.TransformRequest
//     kernel.v1.TransformResponse
//   See seam.md for full sbt-akka-grpc configuration.

import akka.actor.typed.ActorSystem
import akka.actor.typed.scaladsl.Behaviors
import akka.grpc.GrpcClientSettings
import akka.http.scaladsl.Http
import akka.http.scaladsl.server.Directives._
import akka.NotUsed
import akka.stream.scaladsl._
import kernel.v1.{KernelServiceClient, TransformRequest}
import scala.concurrent.{ExecutionContext, Future}
import scala.concurrent.duration._
import scala.util.{Failure, Success}

// InputRecord represents one element in the pipeline — in production this would
// come from Kafka, a database cursor, or another upstream source.
case class InputRecord(id: String, values: Seq[Double], windowSize: Int = 0)

object ScalaPipeline extends App {

  implicit val system: ActorSystem[Nothing] =
    ActorSystem(Behaviors.empty, "scala-pipeline")
  implicit val ec: ExecutionContext = system.executionContext

  // --- gRPC client setup ---

  val kernelAddr = sys.env.getOrElse("RUST_KERNEL_ADDR", "rust-kernel:50051")
  val (kernelHost, kernelPort) = kernelAddr.split(":") match {
    case Array(h, p) => (h, p.toInt)
    case _           => ("rust-kernel", 50051)
  }

  val grpcSettings = GrpcClientSettings
    .connectToServiceAt(kernelHost, kernelPort)
    .withTls(false)  // plaintext for local dev

  val kernelClient: KernelServiceClient = KernelServiceClient(grpcSettings)

  // --- HTTP /healthz endpoint ---

  val httpPort = sys.env.getOrElse("PORT", "8080").toInt

  val routes = get {
    path("healthz") {
      // Probe Rust kernel connectivity by checking the gRPC client state.
      // KernelServiceClient.closed is a Future[Done] that completes on disconnect.
      // For a simple health check we just return ok; in production you would
      // call a lightweight RPC or check the channel state.
      complete("""{"status":"ok"}""")
    }
  }

  Http().newServerAt("0.0.0.0", httpPort).bind(routes).onComplete {
    case Success(binding) =>
      system.log.info(s"HTTP healthz listening on ${binding.localAddress}")
    case Failure(ex) =>
      system.log.error("HTTP server failed to start", ex)
  }

  // --- Akka Streams pipeline ---

  // 5 synthetic InputRecord items for the demo.
  val records: List[InputRecord] = List(
    InputRecord("rec-001", Seq(1.0, 2.0, 3.0, 4.0, 5.0)),
    InputRecord("rec-002", Seq(10.0, 20.0, 30.0, 40.0, 50.0)),
    InputRecord("rec-003", Seq(-1.0, 0.0, 1.0, 2.0, 3.0)),
    InputRecord("rec-004", Seq(100.0, 200.0, 300.0)),
    InputRecord("rec-005", Seq(0.5, 1.5, 2.5, 3.5)),
  )

  val source: Source[InputRecord, NotUsed] = Source(records)

  // kernelFlow is the central Akka Streams + gRPC integration point.
  //
  // mapAsync(parallelism) controls how many gRPC calls are in-flight simultaneously.
  // - parallelism = 1: serial — each element waits for the previous RPC to complete.
  // - parallelism = 2: up to 2 RPCs are in-flight; backpressure applies when both are busy.
  //
  // This is the key mechanism that prevents Scala from overwhelming the Rust service:
  // the Akka Streams backpressure automatically throttles the source when all
  // parallelism slots are occupied.
  val kernelFlow: Flow[InputRecord, (InputRecord, kernel.v1.TransformResponse), NotUsed] =
    Flow[InputRecord].mapAsync(parallelism = 2) { record =>
      val request = TransformRequest(
        operation  = "normalize",
        values     = record.values,
        windowSize = record.windowSize
      )
      kernelClient.transform(request).map(response => (record, response))
    }

  val printSink: Sink[(InputRecord, kernel.v1.TransformResponse), Future[akka.Done]] =
    Sink.foreach { case (record, response) =>
      system.log.info(
        s"id=${record.id} operation=${response.method} " +
        s"result=${response.result.map(d => f"$d%.4f").mkString("[", ", ", "]")} " +
        s"duration_ns=${response.durationNs}"
      )
    }

  val done: Future[akka.Done] = source.via(kernelFlow).runWith(printSink)

  done.onComplete {
    case Success(_) =>
      system.log.info("Pipeline completed successfully")
    case Failure(ex) =>
      system.log.error("Pipeline failed", ex)
  }
}
