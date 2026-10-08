"""Protected local CVM DFP ZIP -> deterministic indicator flow."""
import base64
import binascii
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from .access import authorize_workspace
from .cvm_statements import parse_cvm_archive, MAX_ARCHIVE_BYTES
from .cvm_indicators import calculate_indicators
from .indicator_store import persist_indicators, get_indicators

router=APIRouter(prefix="/v1/workspaces/{workspace_id}",tags=["cvm-indicators"])

class CVMArchiveRequest(BaseModel):
    company_code:str=Field(pattern=r"^\d{1,8}$")
    year:int=Field(ge=2010,le=2100)
    zip_base64:str=Field(min_length=4,max_length=45_000_000)

@router.post("/cvm/dfp/indicators")
def calculate_dfp(workspace_id:str,payload:CVMArchiveRequest,_:str=Depends(authorize_workspace)):
    try:
        raw=base64.b64decode(payload.zip_base64,validate=True)
        if len(raw)>MAX_ARCHIVE_BYTES:
            raise ValueError("archive exceeds safety limit")
        lines=parse_cvm_archive(raw,cvm_code=payload.company_code,year=payload.year,document_type="dfp")
        if not lines:
            return {"status":"insufficient_data","computed":[],"stored":0}
        # CVM archives can contain both individual/consolidated statements and
        # multiple restatements. Never mix them in one ratio calculation.
        groups={}
        for line in lines:
            group=(line.cvm_code,line.reference_date,line.scope,
                   line.dataset_sha256,line.document_type,line.reporting_version)
            groups.setdefault(group,[]).append(line)
        results=[]
        for group, entries in sorted(groups.items()):
            if not group[-1]:
                raise ValueError("missing reporting version; manual restatement review required")
            results.extend(calculate_indicators(entries))
        stored=persist_indicators(workspace_id,results)
        return {"status":"requires_source_review","stored":stored,"computed":[
            {"metric_code":item.metric_code,"value":str(item.value),"scope":item.scope,
             "period":item.period,"formula_version":item.formula_version,
             "source_sha256":item.source_sha256,"account_codes":item.account_codes,
             "status":item.status} for item in results]}
    except (ValueError,binascii.Error) as exc:
        raise HTTPException(status_code=422,detail=str(exc))

@router.get("/cvm/{company_code}/indicators")
def list_dfp(workspace_id:str,company_code:str,_:str=Depends(authorize_workspace)):
    if not company_code.isdecimal() or len(company_code)>8:
        raise HTTPException(status_code=422,detail="invalid company code")
    return {"indicators":get_indicators(workspace_id,company_code)}
