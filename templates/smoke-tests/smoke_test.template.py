{{import_block}}


def test_health_smoke() -> None:
    app = {{app_factory}}()
    client = {{client_factory}}(app)

    response = client.get("{{health_path}}")

    assert response.status_code == 200
