import os
import pytest
from fastapi.testclient import TestClient

# Must set this before importing app
os.environ["TENANTCORE_TEST_SECRET"] = "test-secret-12345"

from src.main import app
from src.auth.middleware import store

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def app_store():
    return store

@pytest.fixture
def super_admin():
    return store.get_user_by_email("superadmin@tenantcore.dev")

@pytest.fixture
def acme_admin():
    return store.get_user_by_email("admin@acme.example")

@pytest.fixture
def acme_member():
    return store.get_user_by_email("alice@acme.example")

@pytest.fixture
def globex_admin():
    return store.get_user_by_email("admin@globex.example")

@pytest.fixture
def globex_member():
    return store.get_user_by_email("carol@globex.example")
