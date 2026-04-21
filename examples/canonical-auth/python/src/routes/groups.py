from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timezone

from src.auth.claims import AuthContext
from src.auth.middleware import require_permission, store, get_auth_context
from src.domain.models import Group, GroupPermission, UserGroup

router = APIRouter()

class CreateGroupRequest(BaseModel):
    name: str
    slug: str
    permissions: Optional[list[str]] = None

class AssignPermissionRequest(BaseModel):
    permission_id: str

class AssignUserRequest(BaseModel):
    user_id: str

@router.get("/groups", dependencies=[Depends(require_permission("iam:group:read"))])
def list_groups(auth: AuthContext = Depends(get_auth_context)):
    tenant_groups = [g for g in store.groups if g.tenant_id == auth.tenant_id]
    return {"groups": tenant_groups}

@router.post("/groups", dependencies=[Depends(require_permission("iam:group:create"))])
def create_group(request: CreateGroupRequest, auth: AuthContext = Depends(get_auth_context)):
    now = datetime.now(timezone.utc).isoformat()
    
    if any(g.tenant_id == auth.tenant_id and g.slug == request.slug for g in store.groups):
        raise HTTPException(status_code=400, detail="Group slug already exists in tenant")
        
    group_id = str(uuid.uuid4())
    new_group = Group(
        id=group_id,
        tenant_id=auth.tenant_id,
        slug=request.slug,
        name=request.name,
        created_at=now
    )
    store.groups.append(new_group)
    
    if request.permissions:
        for perm_name in request.permissions:
            perm = next((p for p in store.permissions if p.name == perm_name), None)
            if not perm:
                raise HTTPException(status_code=400, detail=f"Permission {perm_name} not found")
            store.group_permissions.append(GroupPermission(
                id=str(uuid.uuid4()),
                group_id=group_id,
                permission_id=perm.id,
                granted_at=now
            ))
            
    return new_group

@router.post("/groups/{group_id}/permissions", dependencies=[Depends(require_permission("iam:group:assign_permission"))])
def assign_permission(group_id: str, request: AssignPermissionRequest, auth: AuthContext = Depends(get_auth_context)):
    group = next((g for g in store.groups if g.id == group_id and g.tenant_id == auth.tenant_id), None)
    if not group:
         raise HTTPException(status_code=404, detail="Group not found in your tenant")
         
    perm = next((p for p in store.permissions if p.id == request.permission_id), None)
    if not perm:
         raise HTTPException(status_code=400, detail="Permission not found")
         
    if any(gp.group_id == group_id and gp.permission_id == perm.id for gp in store.group_permissions):
        return {"status": "ok", "message": "Already assigned"}

    now = datetime.now(timezone.utc).isoformat()
    store.group_permissions.append(GroupPermission(
        id=str(uuid.uuid4()),
        group_id=group_id,
        permission_id=perm.id,
        granted_at=now
    ))
    
    # Increment acl_ver for users in this group
    for ug in store.user_groups:
        if ug.group_id == group_id:
            user = store.get_user_by_id(ug.user_id)
            if user:
                user.acl_ver += 1
                
    return {"status": "ok"}

@router.post("/groups/{group_id}/users", dependencies=[Depends(require_permission("iam:group:assign_user"))])
def assign_user(group_id: str, request: AssignUserRequest, auth: AuthContext = Depends(get_auth_context)):
    group = next((g for g in store.groups if g.id == group_id and g.tenant_id == auth.tenant_id), None)
    if not group:
         raise HTTPException(status_code=404, detail="Group not found in your tenant")
         
    if not store.verify_membership(request.user_id, auth.tenant_id):
         raise HTTPException(status_code=404, detail="User not found in your tenant")
         
    if any(ug.group_id == group_id and ug.user_id == request.user_id for ug in store.user_groups):
        return {"status": "ok", "message": "Already assigned"}
        
    now = datetime.now(timezone.utc).isoformat()
    store.user_groups.append(UserGroup(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        group_id=group_id,
        joined_at=now
    ))
    
    user = store.get_user_by_id(request.user_id)
    if user:
        user.acl_ver += 1
        
    return {"status": "ok"}
