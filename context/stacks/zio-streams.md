# ZIO Streams

ZIO Streams is the streaming subsystem of ZIO 2. It provides functional, type-safe stream processing with full integration into ZIO's effect system. Unlike Akka Streams, ZIO Streams has no actor system overhead — it runs on ZIO's fiber-based runtime. It is the natural choice for streaming in ZIO-based Scala services (those using `scala-tapir-http4s-zio.md`).

ZIO Streams exposes three core types:

| Type | Description |
|---|---|
| `ZStream[R, E, A]` | A stream that requires `R`, may fail with `E`, produces elements of type `A` |
| `ZSink[R, E, In, L, Z]` | Consumes a stream and produces a result `Z`; `L` is leftover elements |
| `ZPipeline[R, E, In, Out]` | Transforms a `ZStream[_, _, In]` into a `ZStream[R, E, Out]` |

---

## When ZIO Streams Is the Right Choice

- The service is already built on ZIO 2 (using the `scala-tapir-http4s-zio.md` stack).
- Pure functional effect composition is preferred over Akka's more imperative style.
- Streaming HTTP responses (chunked transfer, server-sent events) from http4s or ZIO HTTP.
- No actor system overhead is needed — ZIO's fiber runtime is lighter than Akka.
- The team wants typed error channels throughout the stream (`ZStream[R, E, A]`).
- Integration with ZIO services: `zio-kafka`, `zio-amqp`, ZIO HTTP streaming endpoints.

---

## When ZIO Streams Is NOT the Right Choice

- The codebase is Akka-based — Akka Streams integrates better with Akka actors and Alpakka connectors.
- Complex graph topologies with fan-out, fan-in, or cycles — Akka `GraphDSL` is more mature for this.
- The team needs Alpakka connectors (Kafka, AMQP, AWS S3, JDBC) — Alpakka only integrates with Akka Streams. ZIO ecosystem has `zio-kafka`, `zio-amqp`, but Alpakka has a larger connector catalog.

---

## Typical Repo Surface

```
build.sbt                                     -- dev.zio::zio-streams, dev.zio::zio
src/main/scala/{domain}/Processor.scala       -- ZStream pipeline definition
src/main/scala/{domain}/Hub.scala             -- fan-out to multiple fibers via Hub
src/main/scala/{domain}/routes/              -- ZIO HTTP streaming endpoints
src/test/scala/{domain}/ProcessorSpec.scala  -- ZIO Test stream tests
```

---

## Core Primitives (ZStream, ZSink, ZPipeline)

### Creating a stream

```scala
import zio._
import zio.stream._

// From an iterable (for tests or demo data)
val fromIterable: ZStream[Any, Nothing, Int] = ZStream.fromIterable(1 to 100)

// From a ZQueue (push-based source)
val fromQueue: ZIO[Any, Nothing, ZStream[Any, Nothing, Event]] =
  Queue.bounded[Event](capacity = 128).map(ZStream.fromQueue(_))

// From a file
val fromFile: ZStream[Any, Throwable, Byte] = ZStream.fromFile(path)

// From a paginated API (cursor-based)
val paginated: ZStream[Any, Throwable, Record] =
  ZStream.paginateZIO(initialCursor)(cursor => fetchPage(cursor))
```

### Running a stream

```scala
// Run with a sink — returns a ZIO effect that produces the sink's result
val program: ZIO[Any, Throwable, Unit] =
  ZStream.fromIterable(1 to 100)
    .map(_ * 1.5)
    .tap(n => ZIO.debug(n.toString))
    .run(ZSink.drain)

// Collect all elements
val all: ZIO[Any, Nothing, Chunk[Int]] =
  ZStream.fromIterable(1 to 10).runCollect
```

### Pipelines

`ZPipeline` is a reusable transformation that can be applied to any compatible stream using `>>>`:

```scala
val normalize: ZPipeline[Any, Nothing, Double, Double] =
  ZPipeline.map(x => if (x == 0.0) 0.0 else x / math.abs(x))

val pipeline: ZStream[Any, Nothing, Double] =
  ZStream.fromIterable(data) >>> normalize

// Chain multiple pipelines
val fullPipeline: ZStream[Any, Throwable, Result] =
  ZStream.fromIterable(rawData) >>> normalize >>> enrich >>> validate
```

---

## Channel and Hub (Fan-Out)

`Hub` broadcasts every published element to **all** subscribers. This is the ZIO equivalent of Akka Streams `Broadcast`:

```scala
for {
  hub <- Hub.bounded[Event](capacity = 64)

  // Two subscribers — each receives every element
  _ <- ZStream.fromHub(hub).run(ZSink.foreach(processForAudit)).fork
  _ <- ZStream.fromHub(hub).run(ZSink.foreach(processForAnalytics)).fork

  // Publish events to all subscribers
  _ <- ZStream.fromIterable(events).foreach(hub.publish)
} yield ()
```

**Hub vs Queue:** `Hub` broadcasts to all subscribers; `Queue` distributes to one consumer at a time (work queue semantics). Use `Hub` for fan-out; use `Queue` for worker pools.

---

## Error Handling in Streams

`ZStream` has a typed error channel `E`. Errors cause the stream to fail and stop by default. Key recovery operators:

```scala
// Recover from any error; switch to a fallback stream
stream.catchAll(e => ZStream.logError(e.getMessage) *> ZStream.empty)

// Retry the failing stream on a schedule
stream.retry(Schedule.exponential(1.second) && Schedule.recurs(3))

// Switch to a fallback stream on failure (shorthand for catchAll)
stream.orElse(fallbackStream)

// Run cleanup effect when the stream ends (success or failure)
stream.ensuring(ZIO.debug("stream finished"))
```

---

## Integration with ZIO HTTP (Streaming HTTP Endpoints)

ZIO HTTP supports streaming responses natively. To stream from an http4s endpoint, convert the `ZStream` to an fs2 stream using `zio-interop-cats`:

```scala
import zio.interop.catz._
import org.http4s._
import org.http4s.dsl.io._
import org.http4s.server.ServerSentEvent

val routes = HttpRoutes.of[Task] {
  case GET -> Root / "events" =>
    val eventStream: ZStream[Any, Nothing, ServerSentEvent] =
      ZStream.fromIterable(events)
        .map(e => ServerSentEvent(Some(e.toJson)))

    Ok(eventStream.toFs2Stream)
}
```

For ZIO HTTP (without http4s), stream a `Body` directly:

```scala
import zio.http._

val app = Http.collect[Request] {
  case Method.GET -> Root / "stream" =>
    Response(
      body = Body.fromStream(
        ZStream.fromIterable("hello world".getBytes).map(Byte.byte2int(_))
      )
    )
}
```

---

## Connecting to External Services

### zio-kafka (canonical Kafka integration for ZIO)

```scala
// deps: dev.zio::zio-kafka
import zio.kafka.consumer._
import zio.kafka.serde._

val stream: ZStream[Consumer, Throwable, CommittableRecord[String, String]] =
  Consumer.subscribeAnd(Subscription.topics("input.topic"))
    .plainStream(Serde.string, Serde.string)

stream
  .mapZIO(record => processEvent(record.value).as(record.offset))
  .aggregateAsync(Consumer.offsetBatches)
  .mapZIO(_.commit)
  .runDrain
```

### zio-amqp (AMQP / RabbitMQ)

```scala
// deps: dev.zio::zio-amqp
import zio.amqp._

val amqpStream: ZStream[AMQPChannel, Throwable, Delivery] =
  AMQPChannel.consume("my.queue")

amqpStream
  .mapZIO(delivery => process(delivery.body).as(delivery))
  .mapZIO(delivery => ZIO.attempt(delivery.ack()))
  .runDrain
```

---

## Testing Expectations

- Use ZIO Test and `ZTestEnvironment` for stream tests.
- Use `ZStream.runCollect` to materialize a stream to a `Chunk[A]` for assertion.
- Prove fan-out with `Hub`: start two subscribers, publish elements, verify each subscriber receives all of them.
- Prove error recovery: inject a failure with `ZStream.fail(e)` and verify `catchAll` fires and produces the expected fallback.
- Prove streaming HTTP: use ZIO HTTP test client or http4s `TestRoutes` to stream from an endpoint and collect the response.
- Run each test in a fresh ZIO runtime to avoid state leakage between tests.

---

## Common Assistant Mistakes

- **Treating `ZStream` as a `ZIO`** — `ZStream` is a description of a stream, not a single effect. Use `.run(sink)` to execute it; just calling `.map()` or `.filter()` does nothing.
- **Not using `.fork` when running multiple streams** — calling `.run()` on a stream blocks the current fiber until the stream completes. Use `.fork` to run streams concurrently.
- **Confusing `Hub` and `Queue`** — `Hub` broadcasts to all subscribers; `Queue` distributes (work queue). Using a `Queue` where a `Hub` is needed silently delivers each element to only one consumer.
- **Not typing the error channel** — using `ZStream[Any, Nothing, A]` when the stream can fail masks real errors. Keep `E` explicit until the application boundary where you convert to `Throwable`.
- **Using `Throwable` as the error type throughout** — define domain-specific error types and map to `Throwable` only at the boundary (e.g., HTTP response encoding, Kafka serialization).
- **Forgetting `runDrain` for side-effecting streams** — a stream with `tap` or `mapZIO` for side effects still does nothing until you call `.runDrain` or `.run(ZSink.drain)`.

---

## Related

- `context/stacks/akka-streams.md` — alternative: Akka Streams for actor-based pipelines with Alpakka connectors
- `context/stacks/scala-tapir-http4s-zio.md` — ZIO HTTP + Tapir for the HTTP service layer
- `context/stacks/kafka.md` — zio-kafka for Kafka integration
- `context/stacks/duo-scala-rust.md` — Scala in the multi-backend context (Akka Streams variant)
