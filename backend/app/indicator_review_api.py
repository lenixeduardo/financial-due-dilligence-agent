"""Local API for explicit, auditable manual review actions."""
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from .access import authorize_workspace
from .reviewer_access import authorize_reviewer
from .indicator_review import review_indicator,list_reviews

router=APIRouter(prefix="/v1/workspaces/{workspace_id}",tags=["indicator-review"])
class ReviewRequest(BaseModel):
    company_code:str=Field(pattern=r"^\d{1,8}$")
    period:str=Field(min_length=10,max_length=10)
    scope:str=Field(pattern=r"^(consolidated|standalone)$")
    metric_code:str=Field(min_length=1,max_length=60)
    formula_version:str=Field(min_length=1,max_length=100)
    dataset_sha256:str=Field(pattern=r"^[0-9a-f]{64}$")
    decision:str=Field(pattern=r"^(approved|rejected)$")
    reviewer:str=Field(min_length=3,max_length=100)
    justification:str=Field(min_length=15,max_length=2000)

@router.post("/cvm/indicators/reviews",status_code=201)
def submit_review(workspace_id:str,payload:ReviewRequest,_:str=Depends(authorize_reviewer)):
    try:
        return review_indicator(workspace_id=workspace_id,**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc))

@router.get("/cvm/{company_code}/reviews")
def get_reviews(workspace_id:str,company_code:str,_:str=Depends(authorize_workspace)):
    if not company_code.isdecimal() or len(company_code)>8:
        raise HTTPException(status_code=422,detail="invalid company")
    return {"events":list_reviews(workspace_id,company_code)}
