"""Local account sign-in. No public self-registration."""
import os
from fastapi import APIRouter,HTTPException,Header
from pydantic import BaseModel,Field
from .user_auth import authenticate,lookup_session,revoke_token
router=APIRouter(prefix="/v1/auth",tags=["authentication"])

class LoginRequest(BaseModel):
    workspace_id:str=Field(min_length=1,max_length=128)
    username:str=Field(min_length=3,max_length=100)
    password:str=Field(min_length=1,max_length=256)

def _bearer(authorization:str|None)->str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401,detail="authentication required")
    return authorization[7:].strip()

@router.post("/login")
def login(payload:LoginRequest):
    if os.getenv("FINSIGHT_AUTH_MODE")!="users":
        raise HTTPException(status_code=503,detail="user authentication is not enabled")
    token=authenticate(workspace_id=payload.workspace_id,username=payload.username,password=payload.password)
    if not token:
        raise HTTPException(status_code=401,detail="invalid credentials")
    return {"access_token":token,"token_type":"bearer","expires_in":28800}

@router.get("/me")
def me(workspace_id:str,authorization:str|None=Header(default=None)):
    session=lookup_session(_bearer(authorization),workspace_id)
    if not session:
        raise HTTPException(status_code=401,detail="authentication required")
    return {"workspace_id":session["workspace_id"],"username":session["username"],"role":session["role"]}

@router.post("/logout")
def logout(authorization:str|None=Header(default=None)):
    revoke_token(_bearer(authorization))
    return {"status":"signed_out"}
