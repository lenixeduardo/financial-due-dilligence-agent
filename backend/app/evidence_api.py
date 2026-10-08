"""Protected evidence endpoints. Users supply text only, not arbitrary fetch URLs."""
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .access import authorize_workspace, authorize_analyst
from .db import insert_evidence, list_evidence
from .evidence import Evidence, retrieve, support_claim

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["evidence"])

class EvidenceInput(BaseModel):
    id: str = Field(min_length=1,max_length=128)
    company_id: str = Field(min_length=1,max_length=128)
    source_url: str = Field(max_length=2048)
    publisher: str = Field(min_length=1,max_length=200)
    document_version: str = Field(min_length=1,max_length=128)
    page: int = Field(ge=1)
    text: str = Field(min_length=1,max_length=50000)

class EvidenceQuery(BaseModel):
    company_id: str = Field(min_length=1,max_length=128)
    query: str = Field(min_length=1,max_length=500)
    limit: int = Field(default=5,ge=1,le=20)

class ClaimQuery(BaseModel):
    company_id: str = Field(min_length=1,max_length=128)
    claim: str = Field(min_length=1,max_length=1000)
    evidence_ids: list[str] = Field(max_length=20)

@router.post("/evidence",status_code=201)
def create_evidence(workspace_id: str, payload: EvidenceInput, _: str = Depends(authorize_analyst)):
    try:
        item = Evidence.create(workspace_id=workspace_id, **payload.model_dump())
        insert_evidence(item)
    except ValueError as err:
        raise HTTPException(status_code=422,detail=str(err))
    return {"id":item.id,"hash":item.sha256_hex,"status":"stored_unverified"}

@router.post("/evidence/search")
def search_evidence(workspace_id: str,payload: EvidenceQuery,_: str = Depends(authorize_workspace)):
    candidates=list_evidence(workspace_id,payload.company_id,limit=100)
    hits=retrieve(payload.query,workspace_id=workspace_id,company_id=payload.company_id,documents=candidates,limit=payload.limit)
    return {"retrieval_method":"lexical_baseline","evidence":[{"id":e.id,"publisher":e.publisher,
            "source_url":e.source_url,"page":e.page,"excerpt":e.text[:1200]} for e in hits]}

@router.post("/claims/check")
def check_claim(workspace_id: str,payload: ClaimQuery,_: str = Depends(authorize_workspace)):
    docs=list_evidence(workspace_id,payload.company_id,limit=100)
    finding=support_claim(payload.claim,payload.evidence_ids,workspace_id=workspace_id,
                          company_id=payload.company_id,documents=docs)
    return {"claim":finding.claim,"citation_ids":finding.evidence_ids,"status":finding.status}
