import pytest
from src.auth.token import issue_token

def test_me_returns_correct_fields(client, acme_member, app_store):
    token = issue_token(acme_member, app_store)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["sub"] == acme_member.id
    assert data["email"] == acme_member.email
    assert data["tenant_id"] == acme_member.tenant_id
    assert "allowed_routes" in data
    assert isinstance(data["allowed_routes"], list)

def test_super_admin_me(client, super_admin, app_store):
    token = issue_token(super_admin, app_store)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["tenant_id"] is None
    assert data["tenant_role"] == "super_admin"
    
    # Ensure allowed routes contains admin routes
    admin_routes = [r for r in data["allowed_routes"] if r["path"].startswith("/admin")]
    assert len(admin_routes) > 0
