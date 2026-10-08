"""Authenticated local ingestion and evidence-only question answering."""
import base64
import binascii
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .access import authorize_workspace, authorize_analyst
from .ingestion import ingest_bytes, MAX_FILE_BYTES
from .analysis import answer_from_evidence

router=APIRouter(prefix="/v1/workspaces/{workspace_id}",tags=["documents"])

class DocumentRequest(BaseModel):
    company_id: str=Field(min_length=1,max_length=128)
    filename: str=Field(min_length=1,max_length=128)
    base64_content: str=Field(min_length=1,max_length=11_000_000)
    source_url: str=Field(min_length=8,max_length=2048,pattern=r"^https://")
    publisher: str=Field(min_length=1,max_length=200)
    document_version: str=Field(min_length=1,max_length=128)

class QuestionRequest(BaseModel):
    company_id: str=Field(min_length=1,max_length=128)
    question: str=Field(min_length=1,max_length=500)

@router.post("/documents/ingest")
def ingest(workspace_id: str,payload:DocumentRequest, _:str=Depends(authorize_analyst)):
    try:
        decoded=base64.b64decode(payload.base64_content,validate=True)
        if len(decoded)>MAX_FILE_BYTES:
            raise ValueError("document exceeds 8 MB")
        return ingest_bytes(workspace_id=workspace_id,company_id=payload.company_id,
           filename=payload.filename,content=decoded,source_url=payload.source_url,
           publisher=payload.publisher,document_version=payload.document_version)
    except (ValueError,binascii.Error) as exc:
        raise HTTPException(status_code=422,detail=str(exc))

@router.post("/analysis/evidence")
def answer(workspace_id:str,payload:QuestionRequest,_:str=Depends(authorize_workspace)):
    try:
        return answer_from_evidence(workspace_id=workspace_id,company_id=payload.company_id,question=payload.question)
    except ValueError as exc:
        raise HTTPException(status_code=422,detail=str(exc))
