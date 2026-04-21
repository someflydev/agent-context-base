import os
import uuid
from datetime import datetime, timezone, timedelta
import jwt

from src.domain.models import User
from src.domain.store import InMemoryStore

# Test mode secret
TEST_SECRET = os.getenv("TENANTCORE_TEST_SECRET")

# Mock RSA keys for production mode
# In a real system, these would be loaded from KMS or a vault.
import cryptography.hazmat.primitives.asymmetric.rsa as rsa
from cryptography.hazmat.primitives import serialization

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_private_key_pem = _private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
# For the mock, just use the generated key. If TEST_SECRET is set, use it.

def get_signing_key():
    if TEST_SECRET:
        return TEST_SECRET, "HS256"
    return _private_key_pem, "RS256"

def get_verification_key():
    if TEST_SECRET:
        return TEST_SECRET, "HS256"
    public_key = _private_key.public_key()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ), "RS256"

def issue_token(user: User, store: InMemoryStore) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=15)
    
    # Extract tenant and membership
    # Assuming user is only in one tenant at a time for this example
    membership = next((m for m in store.memberships if m.user_id == user.id and m.is_active), None)
    
    tenant_id = None
    tenant_role = "tenant_member"
    if membership:
        tenant_id = membership.tenant_id
        tenant_role = membership.tenant_role
    elif user.tenant_id is None: # super_admin
        tenant_role = "super_admin"

    groups = store.get_groups_for_user(user.id, tenant_id)
    permissions = store.get_effective_permissions(user.id)

    if tenant_role == "tenant_admin":
        permissions = [p.name for p in store.permissions]

    # Allow super_admin to have certain explicit capabilities if needed
    if tenant_role == "super_admin":
        permissions = [p.name for p in store.permissions if p.name.startswith("admin:")]
    
    payload = {
        "iss": "tenantcore-auth",
        "aud": "tenantcore-api",
        "sub": user.id,
        "exp": int(exp.timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "jti": str(uuid.uuid4()),
        "tenant_role": tenant_role,
        "groups": [g.slug for g in groups],
        "permissions": permissions,
        "acl_ver": user.acl_ver,
    }
    
    if tenant_id:
        payload["tenant_id"] = tenant_id

    key, alg = get_signing_key()
    return jwt.encode(payload, key, algorithm=alg)
