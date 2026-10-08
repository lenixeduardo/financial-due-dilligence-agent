"""Restricted same-sector or cross-sector comparison; no unverifiable rankings."""
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from .access import authorize_workspace
from .methodologies import Observation,compare
router=APIRouter(prefix="/v1/workspaces/{workspace_id}",tags=["comparison"])
class ComparisonRequest(BaseModel):
    observations:list[Observation]=Field(min_length=2,max_length=50)
@router.post("/comparisons/validate")
def validate_comparison(workspace_id:str,payload:ComparisonRequest,_:str=Depends(authorize_workspace)):
    # Submitted observations are not automatically verified against official sources.
    try:
        result=compare(payload.observations)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc))
    result["evidence_status"]="unverified_user_submitted"
    result["notice"]="Comparative indicators require official-source reconciliation and human review."
    return result
