from datetime import datetime, timezone
import jwt
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.claims import AuthContext
from src.auth.token import get_verification_key
from src.domain.store import InMemoryStore

# Fastapi dep requires store, we use a global store here for simplicity
store = InMemoryStore()

security = HTTPBearer()

def get_auth_context(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthContext:
    token = credentials.credentials
    key, alg = get_verification_key()
    
    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=[alg],
            audience="tenantcore-api",
            issuer="tenantcore-auth",
            options={"require": ["iss", "aud", "sub", "exp", "iat", "nbf", "jti"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    user_id = claims.get("sub")
    user = store.get_user_by_id(user_id)
    
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
        
    if claims.get("acl_ver") != user.acl_ver:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is stale (acl_ver mismatch)")

    tenant_id = claims.get("tenant_id")
    if tenant_id:
        if not store.verify_membership(user.id, tenant_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an active member of the tenant")

    return AuthContext(
        sub=user_id,
        email=user.email,
        tenant_id=tenant_id,
        tenant_role=claims.get("tenant_role", "tenant_member"),
        groups=claims.get("groups", []),
        permissions=claims.get("permissions", []),
        acl_ver=claims.get("acl_ver", 1),
        issued_at=datetime.fromtimestamp(claims.get("iat"), tz=timezone.utc),
        expires_at=datetime.fromtimestamp(claims.get("exp"), tz=timezone.utc),
    )

def require_permission(permission: str):
    def checker(auth: AuthContext = Depends(get_auth_context)):
        if not auth.has_permission(permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return auth
    return checker

def require_super_admin(auth: AuthContext = Depends(get_auth_context)):
    if auth.tenant_role != "super_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return auth
