use std::sync::Arc;
use std::path::Path;
use jsonwebtoken::{EncodingKey, DecodingKey};

use canonical_auth_rust::domain::store::InMemoryStore;
use canonical_auth_rust::create_app;

#[tokio::main]
async fn main() {
    let store = InMemoryStore::load_from_fixtures(Path::new("../../domain/fixtures"))
        .expect("Failed to load fixtures");
    let store = Arc::new(store);

    let encoding_key = EncodingKey::from_secret("dummy".as_bytes());
    let decoding_key = DecodingKey::from_secret("dummy".as_bytes());

    let app = create_app(store, encoding_key, decoding_key);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
