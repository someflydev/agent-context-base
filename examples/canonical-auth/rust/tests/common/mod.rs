use std::sync::Arc;
use std::path::Path;

use axum::Router;
use jsonwebtoken::{EncodingKey, DecodingKey};
use serde_json::Value;

use canonical_auth_rust::create_app;
use canonical_auth_rust::domain::store::InMemoryStore;

pub fn setup_test_app() -> (Router, Arc<InMemoryStore>, Vec<u8>) {
    std::env::set_var("TENANTCORE_TEST_SECRET", "test-secret");
    let secret = b"test-secret".to_vec();

    let store = InMemoryStore::load_from_fixtures(Path::new("../domain/fixtures"))
        .expect("Failed to load fixtures");
    let store = Arc::new(store);

    let encoding_key = EncodingKey::from_secret(&secret);
    let decoding_key = DecodingKey::from_secret(&secret);

    let app = create_app(store.clone(), encoding_key, decoding_key);
    
    (app, store, secret)
}
