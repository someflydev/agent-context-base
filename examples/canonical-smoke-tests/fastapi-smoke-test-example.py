from fastapi.testclient import TestClient

from app.main import create_app


def test_health_smoke() -> None:
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_report_summary_smoke() -> None:
    client = TestClient(create_app())

    response = client.get("/reports/summary", params={"tenant_id": "acme", "limit": 5})

    assert response.status_code == 200
    assert isinstance(response.json(), list)

