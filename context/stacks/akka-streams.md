# Akka Streams

Akka Streams is the Scala streaming library for building reactive, backpressure-aware stream topologies. It is built on top of Akka (or Apache Pekko) actors and implements the Reactive Streams specification. It is used in Scala services — especially for the duo-scala-rust and trio-elixir-go-rust patterns — where a streaming topology must delegate hot-path compute to an external service via gRPC.

> **Scala 3 / Lightbend licensing note:** For teams on Scala 3 or teams avoiding Lightbend commercial licensing, consider **Apache Pekko**, a direct fork of Akka Streams with the same API under the Apache 2.0 license. The code examples in this doc apply to both Akka and Pekko — substitute `org.apache.pekko` for `com.typesafe.akka` in `build.sbt`.

---

## When Akka Streams Is the Right Choice

- Building a multi-stage processing pipeline where each stage can have different concurrency, throttling, or parallelism requirements.
- Streaming data with backpressure semantics where producers must not overwhelm consumers.
- Complex topologies with fan-out (`Broadcast`), fan-in (`Merge`, `Zip`), or cycles (`GraphDSL`).
- Connecting multiple sources (HTTP, Kafka, file, NATS) into a unified processing graph.
- The team already uses Akka/Pekko for actor-based coordination.
- Integrating with Alpakka connectors (Kafka, AMQP, AWS S3, JDBC, gRPC).
- Delegating hot-path compute stages to a Rust gRPC kernel via `mapAsync`.

---

## When Akka Streams Is NOT the Right Choice

- Simple sequential data processing where ZIO Streams or fs2 would be lighter — no actor system overhead required.
- The team is not on Akka/Pekko — for a pure-functional alternative, use ZIO Streams or fs2.
- The streaming workload is stateless and high-throughput without complex topology — Kafka consumer groups may be sufficient.
- Scala 3 is the target without legacy Akka Classic — prefer Pekko or ZIO Streams to avoid Lightbend licensing concerns.

---

## Typical Repo Surface

```
build.sbt                                       -- com.typesafe.akka::akka-stream, akka-actor-typed
src/main/scala/{domain}/Pipeline.scala          -- source → flow → sink chain
src/main/scala/{domain}/StreamGraphs.scala      -- complex topologies using GraphDSL
src/main/scala/{domain}/KernelClient.scala      -- gRPC client for delegating to Rust kernel
src/test/scala/{domain}/PipelineSpec.scala      -- AkkaSpec-based stream tests
```

---

## Core Primitives (Source, Flow, Sink, RunnableGraph)

| Type | Description |
|---|---|
| `Source[T, Mat]` | Produces elements of type `T` |
| `Flow[In, Out, Mat]` | Transforms elements from `In` to `Out` |
| `Sink[In, Mat]` | Consumes elements of type `In` |
| `RunnableGraph[Mat]` | A connected `Source → Sink` graph ready to materialize |

The third type parameter (`Mat`) is the **materialized value** — see the next section.

Minimal example:

```scala
import akka.actor.ActorSystem
import akka.stream.scaladsl._
import akka.NotUsed
import scala.concurrent.Future
import akka.Done

implicit val system: ActorSystem = ActorSystem("pipeline")

val source: Source[Int, NotUsed]       = Source(1 to 100)
val flow:   Flow[Int, Double, NotUsed] = Flow[Int].map(n => n * 1.5)
val sink:   Sink[Double, Future[Done]] = Sink.foreach(println)

source.via(flow).runWith(sink)
// Returns: Future[Done] — completes when the stream finishes
```

---

## Materialized Values

The third type parameter in `Source`/`Flow`/`Sink` is the materialized value — the value produced **when the graph is run**. It is not an element in the stream; it is a side-channel result from the operator's lifecycle.

Common materialized values:

| Sink | Materialized value |
|---|---|
| `Sink.head` | `Future[T]` — the first emitted element |
| `Sink.fold` | `Future[U]` — accumulated result |
| `Sink.seq` | `Future[Seq[T]]` — all elements collected |
| `Sink.queue` | `SinkQueueWithCancel` — allow imperative pull |
| `Source.queue` | `SourceQueueWithComplete` — allow imperative push |

When composing `source.via(flow).runWith(sink)`, the materialized value is that of the **Sink** (right side). Use `.toMat(sink)(Keep.both)` to preserve both materialized values:

```scala
val (sourceQueue, doneFuture) =
  Source.queue[Event](bufferSize = 128)
    .via(myFlow)
    .toMat(Sink.foreach(publish))(Keep.both)
    .run()
```

---

## Backpressure and Demand Signaling

Akka Streams implements the [Reactive Streams](https://www.reactive-streams.org/) specification. When a downstream operator is slower than upstream, it **signals demand upstream** and the source slows automatically. There is no need to manually handle overflow for most use cases.

Key operators for controlling backpressure:

```scala
// Buffer n elements; if the buffer is full, signal demand stop to the upstream.
source.buffer(n = 64, OverflowStrategy.backpressure)

// Rate limiting: allow up to `elements` per `per` duration, with bursting.
source.throttle(elements = 100, per = 1.second, burst = 10, mode = ThrottleMode.Shaping)

// Merge slow-consumer messages using a function (lossy — use with care).
source.conflate((acc, next) => acc.merge(next))
```

---

## GraphDSL for Complex Topologies

Use `GraphDSL` when the topology cannot be expressed as a linear `source → flow → sink` chain — for example, fan-out to two parallel flows that merge back together:

```scala
import akka.stream.{ClosedShape}
import akka.stream.scaladsl.GraphDSL.Implicits._

val graph = RunnableGraph.fromGraph(GraphDSL.create() { implicit b =>
  val broadcast = b.add(Broadcast[Event](2))
  val merge     = b.add(Merge[ProcessedEvent](2))

  source     ~> broadcast
  broadcast  ~> fastFlow  ~> merge
  broadcast  ~> slowFlow  ~> merge
                             merge ~> sink
  ClosedShape
})

graph.run()
```

Other useful `GraphDSL` shapes:

| Shape | Description |
|---|---|
| `Broadcast[T](n)` | Fan-out: sends every element to all `n` outputs |
| `Merge[T](n)` | Fan-in: interleaves elements from `n` inputs |
| `Zip[A, B]` | Pairs elements from two inputs into `(A, B)` |
| `Balance[T](n)` | Distributes elements across `n` outputs (work stealing) |
| `Concat[T]` | Drains the first source, then switches to the second |

---

## Connecting to External Services (gRPC, HTTP, Kafka)

### gRPC with Akka gRPC (sbt-akka-grpc)

Akka gRPC generates Scala stubs from `.proto` files and provides streaming gRPC support. The generated stubs integrate naturally with Akka Streams — streaming RPCs return `Source[Response, NotUsed]` or accept `Source[Request, NotUsed]`.

Add to `build.sbt`:

```scala
enablePlugins(AkkaGrpcPlugin)

libraryDependencies += "com.lightbend.akka.grpc" %% "akka-grpc-runtime" % "2.4.0"
```

The central Akka Streams integration point is `mapAsync` — it calls the gRPC RPC for each element and controls the concurrency of concurrent in-flight calls:

```scala
// mapAsync(parallelism) controls how many gRPC calls are in-flight simultaneously.
// If parallelism = 1, the stream is serial: each element waits for the previous RPC.
// If parallelism = 4, up to 4 RPCs are in-flight; backpressure applies when all 4 are busy.
val kernelFlow: Flow[InputRecord, KernelResult, NotUsed] =
  Flow[InputRecord].mapAsync(parallelism = 4) { record =>
    val request = TransformRequest(
      operation  = "normalize",
      values     = record.values,
      windowSize = record.windowSize
    )
    kernelClient.transform(request)  // returns Future[TransformResponse]
  }
```

### Kafka with Alpakka Kafka

```scala
// deps: com.typesafe.akka::akka-stream-kafka
import akka.kafka.scaladsl._
import akka.kafka._

val kafkaSource: Source[ConsumerMessage.CommittableMessage[String, Array[Byte]], Consumer.Control] =
  Consumer.committableSource(consumerSettings, Subscriptions.topics("input.topic"))

kafkaSource
  .mapAsync(parallelism = 4) { msg => processEvent(msg.record.value()).map(_ => msg.committableOffset) }
  .runWith(Committer.sink(CommitterSettings(system)))
```

---

## Local Dev Composition

Akka Streams services run in JVM containers. Key considerations:

- JVM startup takes longer than Go/Rust — set `start_period: 40s` in healthchecks.
- Set JVM heap in `JAVA_OPTS`: `-Xmx512m -Xms256m` for dev containers.
- Use `eclipse-temurin:21-jre-alpine` or `openjdk:21-slim` as base image.
- Use `sbt assembly` to build a fat JAR for Docker.

```yaml
services:
  scala-pipeline:
    build:
      context: ./services/pipeline
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      RUST_KERNEL_ADDR: "rust-kernel:50051"
      JAVA_OPTS: "-Xmx512m"
    depends_on:
      rust-kernel:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 40s
```

---

## Testing Expectations

- Use `AkkaSpec` or `ScalaTestWithActorTestKit` for stream tests; create `ActorSystem` once per test suite, not per test.
- Prove a `Source → Flow → Sink` pipeline with a real graph — run it with `runWith` and assert the materialized `Future` result.
- Prove backpressure: use a slow `Sink` (e.g., `Sink.lazyInit` with a delay) and verify the source throttles or the buffer fills.
- Prove `GraphDSL` broadcast/merge topologies by asserting element counts on each branch.
- Prove gRPC integration: use a test gRPC server (testcontainers or an embedded in-process server) — do not mock the stub.
- Keep stream tests deterministic: avoid time-based assertions; prefer element count assertions with `Sink.seq` → `Future[Seq[T]]`.

---

## Common Assistant Mistakes

- **Creating `ActorSystem` on every test** — `ActorSystem` is expensive to start. Create one per test suite in `beforeAll`; shut it down in `afterAll`.
- **Not materializing the graph** — calling `.via()` or `.to()` builds the graph description but does NOT run the stream. Call `.run()` or `.runWith(sink)` to start it.
- **Forgetting to shut down `ActorSystem` in tests** — causes resource leaks and hanging test suites. Always call `system.terminate()` in teardown.
- **Using `Sink.foreach` for async side effects in production code** — `Sink.foreach` is synchronous inside the lambda; use `Sink.foreachAsync` for async side effects.
- **Ignoring materialized values** — if you want the result of a `Sink`, capture the materialized value returned by `.run()` / `.runWith()`. Discarding it silently loses the result.
- **Using Akka Classic instead of Akka Typed** when starting a new service — prefer `ActorSystem[T]` from `akka-actor-typed`.

---

## Related

- `context/stacks/zio-streams.md` — alternative: ZIO 2 Streams for pure-functional approach with no actor system overhead
- `context/stacks/scala-tapir-http4s-zio.md` — ZIO HTTP + Tapir for Scala HTTP services
- `context/stacks/grpc.md` — gRPC seam; Akka gRPC (sbt-akka-grpc) generates streaming-capable stubs
- `context/stacks/kafka.md` — Alpakka Kafka for Kafka Streams in Akka
- `context/stacks/duo-scala-rust.md` — Scala Akka Streams + Rust kernel gRPC seam
- `context/stacks/trio-scala-python-go.md` — Scala in a three-service pipeline
- `examples/canonical-multi-backend/duos/scala-rust-grpc/` — canonical Akka Streams gRPC seam example
