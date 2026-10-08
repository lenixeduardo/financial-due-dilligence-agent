"""Fail-closed access helpers. Production identity provider integration pending."""
import hmac
import os
from fastapi import Header, HTTPException

def authorize_workspace(workspace_id: str, x_workspace_key: str | None = Header(default=None)):
    """Single-workspace deployment key: disabled if not explicitly configured."""
    configured = os.getenv("FINSIGHT_WORKSPACE_API_KEY")
    configured_workspace = os.getenv("FINSIGHT_WORKSPACE_ID")
    if not configured or not configured_workspace or not x_workspace_key or workspace_id != configured_workspace:
        raise HTTPException(status_code=403, detail="workspace access denied")
    if not hmac.compare_digest(x_workspace_key, configured):
        raise HTTPException(status_code=403, detail="workspace access denied")
    return workspace_id
