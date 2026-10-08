"""Fail-closed workspace authorization: user sessions in production, local key in development."""
import hmac
import os
from fastapi import Header, HTTPException
from .user_auth import lookup_session

def workspace_identity(workspace_id:str,authorization:str|None=None,
                       x_workspace_key:str|None=None)->dict:
    if os.getenv("FINSIGHT_AUTH_MODE")=="users":
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401,detail="user authentication required")
        session=lookup_session(authorization[7:].strip(),workspace_id)
        if not session:
            raise HTTPException(status_code=403,detail="workspace access denied")
        return session
    if os.getenv("FINSIGHT_ENV")=="production":
        raise HTTPException(status_code=503,detail="production requires user authentication")
    configured=os.getenv("FINSIGHT_WORKSPACE_API_KEY")
    configured_workspace=os.getenv("FINSIGHT_WORKSPACE_ID")
    if not configured or not configured_workspace or not x_workspace_key or workspace_id!=configured_workspace:
        raise HTTPException(status_code=403,detail="workspace access denied")
    if not hmac.compare_digest(x_workspace_key,configured):
        raise HTTPException(status_code=403,detail="workspace access denied")
    return {"workspace_id":workspace_id,"username":"local-unverified","role":"admin"}

def authorize_workspace(workspace_id:str,x_workspace_key:str|None=Header(default=None),
                        authorization:str|None=Header(default=None)):
    workspace_identity(workspace_id,authorization,x_workspace_key)
    return workspace_id
