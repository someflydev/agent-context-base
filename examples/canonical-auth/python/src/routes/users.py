from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone

from src.auth.claims import AuthContext
from src.auth.middleware import require_permission, store, get_auth_context
from src.domain.models import User, Membership, UserGroup

router = APIRouter()

class InviteRequest(BaseModel):
    email: str
    display_name: str
    group_slugs: Optional[list[str]] = None

class UpdateRequest(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/users", dependencies=[Depends(require_permission("iam:user:read"))])
def list_users(auth: AuthContext = Depends(get_auth_context)):
    tenant_users = [
        u for u in store.users 
        if u.tenant_id == auth.tenant_id or any(m.tenant_id == auth.tenant_id and m.is_active for m in store.memberships if m.user_id == u.id)
    ]
    return {"users": tenant_users}

@router.post("/users", dependencies=[Depends(require_permission("iam:user:invite"))])
def invite_user(request: InviteRequest, auth: AuthContext = Depends(get_auth_context)):
    now = datetime.now(timezone.utc).isoformat()
    
    # Simple check if email exists in whole system
    existing_user = store.get_user_by_email(request.email)
    if existing_user:
        if existing_user.tenant_id == auth.tenant_id:
            raise HTTPException(status_code=400, detail="User already in tenant")
        raise HTTPException(status_code=400, detail="User email already taken globally")
        
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=request.email,
        display_name=request.display_name,
        tenant_id=auth.tenant_id,
        is_active=True,
        acl_ver=1,
        created_at=now
    )
    store.users.append(new_user)
    
    membership_id = str(uuid.uuid4())
    new_membership = Membership(
        id=membership_id,
        user_id=user_id,
        tenant_id=auth.tenant_id,
        tenant_role="tenant_member",
        is_active=True,
        created_at=now
    )
    store.memberships.append(new_membership)
    
    if request.group_slugs:
        for slug in request.group_slugs:
            group = next((g for g in store.groups if g.tenant_id == auth.tenant_id and g.slug == slug), None)
            if group:
                store.user_groups.append(UserGroup(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    group_id=group.id,
                    joined_at=now
                ))
    
    return new_user

@router.get("/users/{user_id}", dependencies=[Depends(require_permission("iam:user:read"))])
def get_user(user_id: str, auth: AuthContext = Depends(get_auth_context)):
    user = store.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not store.verify_membership(user_id, auth.tenant_id):
         raise HTTPException(status_code=403, detail="Forbidden: User not in your tenant")
    return user

@router.patch("/users/{user_id}", dependencies=[Depends(require_permission("iam:user:update"))])
def update_user(user_id: str, request: UpdateRequest, auth: AuthContext = Depends(get_auth_context)):
    user = store.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not store.verify_membership(user_id, auth.tenant_id):
         raise HTTPException(status_code=403, detail="Forbidden: User not in your tenant")
         
    if request.display_name is not None:
        user.display_name = request.display_name
    if request.is_active is not None:
        user.is_active = request.is_active
        
    user.acl_ver += 1
    return user
