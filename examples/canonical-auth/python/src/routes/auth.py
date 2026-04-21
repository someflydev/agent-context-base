from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.auth.token import issue_token
from src.auth.middleware import store

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/token")
def login(request: LoginRequest):
    user = store.get_user_by_email(request.email)
    
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
    # In a real app, verify password hash. Here we trust the email.
    if request.password != "password":  # mock password validation
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
    token = issue_token(user, store)
    return {"access_token": token, "token_type": "bearer"}
