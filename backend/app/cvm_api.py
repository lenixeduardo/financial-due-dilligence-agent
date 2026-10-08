"""Explicit, protected CVM ingestion endpoint; disabled unless opted in."""
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from .access import authorize_workspace, authorize_analyst
from .cvm_collection import collect_cvm_document

router=APIRouter(prefix="/v1/workspaces/{workspace_id}",tags=["official-sources"])

class CVMRequest(BaseModel):
    company_id:str=Field(min_length=1,max_length=128)
    url:str=Field(min_length=25,max_length=2048)
    document_version:str=Field(min_length=1,max_length=128)

@router.post("/sources/cvm/collect")
def collect(workspace_id:str,payload:CVMRequest,_:str=Depends(authorize_analyst)):
    try:
        return collect_cvm_document(workspace_id=workspace_id,company_id=payload.company_id,
              url=payload.url,document_version=payload.document_version)
    except (ValueError,RuntimeError) as error:
        raise HTTPException(status_code=422,detail=str(error))
