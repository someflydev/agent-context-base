from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone

from src.auth.claims import AuthContext
from src.auth.middleware import require_super_admin, store, get_auth_context
from src.domain.models import Tenant, User, Membership

router = APIRouter()

class CreateTenantRequest(BaseModel):
    name: str
    slug: str
    admin_email: str

@router.get("/admin/tenants", dependencies=[Depends(require_super_admin)])
def list_tenants(auth: AuthContext = Depends(get_auth_context)):
    return {"tenants": store.tenants}

@router.post("/admin/tenants", dependencies=[Depends(require_super_admin)])
def create_tenant(request: CreateTenantRequest, auth: AuthContext = Depends(get_auth_context)):
    now = datetime.now(timezone.utc).isoformat()
    
    if any(t.slug == request.slug for t in store.tenants):
        raise HTTPException(status_code=400, detail="Tenant slug already exists")
        
    tenant_id = str(uuid.uuid4())
    new_tenant = Tenant(
        id=tenant_id,
        slug=request.slug,
        name=request.name,
        is_active=True,
        created_at=now
    )
    store.tenants.append(new_tenant)
    
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=request.admin_email,
        display_name="Admin",
        tenant_id=tenant_id,
        is_active=True,
        acl_ver=1,
        created_at=now
    )
    store.users.append(new_user)
    
    store.memberships.append(Membership(
        id=str(uuid.uuid4()),
        user_id=user_id,
        tenant_id=tenant_id,
        tenant_role="tenant_admin",
        is_active=True,
        created_at=now
    ))
    
    return new_tenant
