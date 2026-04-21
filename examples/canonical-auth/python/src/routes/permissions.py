from fastapi import APIRouter, Depends

from src.auth.claims import AuthContext
from src.auth.middleware import require_permission, store, get_auth_context

router = APIRouter()

@router.get("/permissions", dependencies=[Depends(require_permission("iam:permission:read"))])
def list_permissions(auth: AuthContext = Depends(get_auth_context)):
    return {"permissions": store.permissions}
