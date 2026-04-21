import jwt
from datetime import datetime, timezone
import os

from src.auth.token import issue_token, get_verification_key

def test_issue_token_valid(acme_member, app_store):
    token = issue_token(acme_member, app_store)
    assert token is not None
    
    key, alg = get_verification_key()
    claims = jwt.decode(token, key, algorithms=[alg], audience="tenantcore-api")
    
    assert claims["iss"] == "tenantcore-auth"
    assert claims["aud"] == "tenantcore-api"
    assert claims["sub"] == acme_member.id
    
    # Expiry should be exactly 15 minutes (900 seconds) from issue
    assert claims["exp"] - claims["iat"] == 900
    
    assert claims["tenant_id"] == acme_member.tenant_id
    assert claims["tenant_role"] == "tenant_member"
    
    # Alice is in some groups and has some permissions according to the fixtures
    assert "groups" in claims
    assert "permissions" in claims
    assert claims["acl_ver"] == acme_member.acl_ver

def test_super_admin_token(super_admin, app_store):
    token = issue_token(super_admin, app_store)
    
    key, alg = get_verification_key()
    claims = jwt.decode(token, key, algorithms=[alg], audience="tenantcore-api")
    
    assert "tenant_id" not in claims
    assert claims["tenant_role"] == "super_admin"
