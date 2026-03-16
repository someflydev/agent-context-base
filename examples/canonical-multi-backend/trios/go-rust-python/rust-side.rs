// Seam example: Rust preprocessing kernel — tonic gRPC server
// This file shows only the seam layer: gRPC server setup, Preprocess RPC
// implementation, and HTTP health sidecar. Not a full application.
// See context/stacks/trio-go-rust-python.md for architecture context.
//
// Build: cargo build --release
// The build.rs file (not shown) calls: tonic_build::compile_protos("service.proto")
//
// Environment variables:
//   GRPC_PORT  — gRPC listen port (default 50051)
//   HTTP_PORT  — HTTP healthz sidecar port (default 8090)

use std::env;
use std::net::SocketAddr;
use tonic::{transport::Server, Request, Response, Status};
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

// Generated from service.proto by tonic_build in build.rs
pub mod processing {
    tonic::include_proto!("processing.v1");
}

use processing::process_service_server::{ProcessService, ProcessServiceServer};
use processing::{PreprocessRequest, PreprocessResponse};

#[derive(Default)]
pub struct ProcessServiceImpl;

#[tonic::async_trait]
impl ProcessService for ProcessServiceImpl {
    // Seam A↔B: Go calls this RPC via gRPC
    // Stub implementation: splits on whitespace, uses word length as feature value
    async fn preprocess(
        &self,
        request: Request<PreprocessRequest>,
    ) -> Result<Response<PreprocessResponse>, Status> {
        let req = request.into_inner();

        let tokens: Vec<&str> = if req.document.is_empty() {
            vec![]
        } else {
            req.document.split_whitespace().collect()
        };

        let features: Vec<f64> = tokens
            .iter()
            .map(|t| t.len() as f64)
            .collect();

        let token_count = tokens.len() as i32;

        eprintln!(
            "preprocess doc_id={} token_count={} features={:?}",
            req.doc_id, token_count, features
        );

        Ok(Response::new(PreprocessResponse {
            features,
            token_count,
        }))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let grpc_port: u16 = env::var("GRPC_PORT")
        .unwrap_or_else(|_| "50051".to_string())
        .parse()?;
    let http_port: u16 = env::var("HTTP_PORT")
        .unwrap_or_else(|_| "8090".to_string())
        .parse()?;

    let grpc_addr: SocketAddr = format!("0.0.0.0:{}", grpc_port).parse()?;

    // Spawn HTTP health sidecar on a separate tokio task
    tokio::spawn(async move {
        serve_healthz(http_port).await;
    });

    eprintln!("rust-service gRPC listening on {}", grpc_addr);
    Server::builder()
        .add_service(ProcessServiceServer::new(ProcessServiceImpl::default()))
        .serve(grpc_addr)
        .await?;

    Ok(())
}

// Minimal HTTP server for /healthz — runs alongside the gRPC server
async fn serve_healthz(port: u16) {
    let listener = TcpListener::bind(format!("0.0.0.0:{}", port))
        .await
        .expect("failed to bind healthz port");
    eprintln!("rust-service healthz HTTP on :{}", port);

    loop {
        if let Ok((mut stream, _)) = listener.accept().await {
            tokio::spawn(async move {
                let mut buf = [0u8; 1024];
                let _ = stream.read(&mut buf).await;
                let body = r#"{"status":"ok"}"#;
                let response = format!(
                    "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}",
                    body.len(),
                    body
                );
                let _ = stream.write_all(response.as_bytes()).await;
            });
        }
    }
}
