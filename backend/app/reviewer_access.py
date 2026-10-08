"""Separate review permission from general workspace reads.

Still a single shared local reviewer credential, not a user identity provider.
"""
import hmac
import os
from fastapi import Header, HTTPException
from .access import authorize_workspace

def authorize_reviewer(workspace_id: str,
                       x_workspace_key: str | None=Header(default=None),
                       x_review_key: str | None=Header(default=None)):
    # Reuse existing fail-closed workspace isolation.
    authorize_workspace(workspace_id, x_workspace_key)
    configured=os.getenv("FINSIGHT_REVIEW_API_KEY")
    general=os.getenv("FINSIGHT_WORKSPACE_API_KEY")
    if (not configured or not x_review_key or configured==general
            or not hmac.compare_digest(configured,x_review_key)):
        raise HTTPException(status_code=403,detail="review permission denied")
    return workspace_id
