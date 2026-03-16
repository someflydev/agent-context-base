// This is a seam-focused example.
// For a full application scaffold, see context/archetypes/multi-backend-service.md.
//
// kotlin-caller.kt — Kotlin service: calls the Rust ComputeService via gRPC,
// prints the response, and exposes a /healthz HTTP endpoint via Ktor that
// probes the Rust gRPC health check.
//
// build.gradle.kts dependencies:
//   implementation("io.grpc:grpc-kotlin-stub:1.4.1")
//   implementation("io.grpc:grpc-netty-shaded:1.67.1")
//   implementation("com.google.protobuf:protobuf-kotlin:4.28.3")
//   implementation("io.ktor:ktor-server-netty:2.3.12")
//   implementation("io.ktor:ktor-server-core:2.3.12")
//   implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")

import compute.v1.ComputeRequest
import compute.v1.ComputeServiceGrpcKt
import compute.v1.HealthCheckRequest
import io.grpc.ManagedChannelBuilder
import io.grpc.StatusException
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.coroutines.runBlocking

fun main() = runBlocking {
    val rustAddr = System.getenv("RUST_GRPC_URL") ?: "rust-service:50051"
    val httpPort = System.getenv("PORT")?.toIntOrNull() ?: 8080

    val (host, port) = parseGrpcAddr(rustAddr)
    val channel = ManagedChannelBuilder.forAddress(host, port)
        .usePlaintext()
        .build()
    val stub = ComputeServiceGrpcKt.ComputeServiceCoroutineStub(channel)

    // Demonstrate the seam: send a ComputeRequest to Rust and print the response.
    val sampleValues = listOf(1.0, 2.0, 3.0, 4.0, 5.0)
    try {
        val response = stub.compute(
            ComputeRequest.newBuilder()
                .setMethod("mean")
                .addAllValues(sampleValues)
                .setN(0)
                .build()
        )
        println("Rust response: result=${response.result} method=${response.method} duration_ns=${response.durationNs}")
    } catch (e: StatusException) {
        System.err.println("gRPC call failed: ${e.status}")
    }

    // Start Ktor HTTP server with /healthz that probes the Rust gRPC health check.
    val server = embeddedServer(Netty, port = httpPort) {
        routing {
            get("/healthz") {
                val rustHealthy = checkRustHealth(stub)
                if (rustHealthy) {
                    call.respondText("""{"status":"ok"}""", status = io.ktor.http.HttpStatusCode.OK)
                } else {
                    call.respondText(
                        """{"status":"degraded","reason":"rust compute unreachable"}""",
                        status = io.ktor.http.HttpStatusCode.ServiceUnavailable
                    )
                }
            }
        }
    }
    println("Ktor HTTP listening on :$httpPort")
    server.start(wait = true)

    channel.shutdown()
}

suspend fun checkRustHealth(stub: ComputeServiceGrpcKt.ComputeServiceCoroutineStub): Boolean {
    return try {
        val resp = stub.check(HealthCheckRequest.newBuilder().setService("").build())
        resp.status.number == 1 // ServingStatus.SERVING = 1
    } catch (e: StatusException) {
        System.err.println("health check failed: ${e.status}")
        false
    }
}

fun parseGrpcAddr(addr: String): Pair<String, Int> {
    val parts = addr.split(":")
    return if (parts.size == 2) {
        Pair(parts[0], parts[1].toIntOrNull() ?: 50051)
    } else {
        Pair(addr, 50051)
    }
}
