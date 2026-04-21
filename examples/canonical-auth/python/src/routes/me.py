from fastapi import APIRouter, Depends

from src.auth.claims import AuthContext
from src.auth.middleware import get_auth_context, store
from src.registry.routes import get_allowed_routes

router = APIRouter()

@router.get("/me")
def get_me(auth: AuthContext = Depends(get_auth_context)):
    user = store.get_user_by_id(auth.sub)
    if not user:
        # Should be caught by middleware but safe to check
        return {"error": "User not found"}
        
    tenant_name = store.get_tenant_name(auth.tenant_id) if auth.tenant_id else None
    
    is_super_admin = auth.tenant_role == "super_admin"
    allowed_routes = get_allowed_routes(auth.permissions, is_super_admin)
    
    guide_sections = list(set([r.get("description", "") for r in allowed_routes if "description" in r]))
    
    return {
        "sub": auth.sub,
        "email": auth.email,
        "display_name": user.display_name,
        "tenant_id": auth.tenant_id,
        "tenant_name": tenant_name,
        "tenant_role": auth.tenant_role,
        "groups": auth.groups,
        "permissions": auth.permissions,
        "acl_ver": auth.acl_ver,
        "allowed_routes": allowed_routes,
        "guide_sections": guide_sections,
        "issued_at": auth.issued_at.isoformat().replace("+00:00", "Z"),
        "expires_at": auth.expires_at.isoformat().replace("+00:00", "Z")
    }
