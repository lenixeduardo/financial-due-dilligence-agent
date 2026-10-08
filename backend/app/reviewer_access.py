"""Reviewer RBAC for user sessions; legacy separate key for local development only."""
import hmac
import os
from fastapi import Header, HTTPException
from .access import workspace_identity

def authorize_reviewer(workspace_id:str,
                       x_workspace_key:str|None=Header(default=None),
                       x_review_key:str|None=Header(default=None),
                       authorization:str|None=Header(default=None)):
    claims=workspace_identity(workspace_id,authorization,x_workspace_key)
    if os.getenv("FINSIGHT_AUTH_MODE")=="users":
        if claims["role"] not in ("reviewer","admin"):
            raise HTTPException(status_code=403,detail="review permission denied")
        return claims
    configured=os.getenv("FINSIGHT_REVIEW_API_KEY")
    general=os.getenv("FINSIGHT_WORKSPACE_API_KEY")
    if (not configured or not x_review_key or configured==general
            or not hmac.compare_digest(configured,x_review_key)):
        raise HTTPException(status_code=403,detail="review permission denied")
    return claims
