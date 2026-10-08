"""Opt-in CVM document fetch into SQLite. No untrusted URL input."""
import os
from urllib.parse import urlparse
from .sources import download_official, validate_url
from .ingestion import ingest_bytes

BASE="https://dados.cvm.gov.br/"
ALLOWED_PREFIXES=(
    "/dados/CIA_ABERTA/DOC/DFP/DADOS/",
    "/dados/CIA_ABERTA/DOC/ITR/DADOS/",
    "/dados/CIA_ABERTA/CAD/DADOS/",
)
ALLOWED_EXTENSIONS=(".csv",".txt",".pdf")

def validate_cvm_document(url: str) -> str:
    validate_url(url)
    parts=urlparse(url)
    if parts.hostname!="dados.cvm.gov.br" or parts.query or parts.fragment:
        raise ValueError("only direct CVM document URLs are accepted")
    if not any(parts.path.startswith(prefix) for prefix in ALLOWED_PREFIXES):
        raise ValueError("CVM document path not approved")
    if not parts.path.lower().endswith(ALLOWED_EXTENSIONS):
        raise ValueError("only approved PDF, CSV, TXT resources are supported")
    if ".." in parts.path or "%2" in parts.path.lower():
        raise ValueError("ambiguous or encoded path")
    return url

def collect_cvm_document(*,workspace_id:str,company_id:str,url:str,
                         document_version:str,fetcher=download_official)->dict:
    if os.getenv("FINSIGHT_ENABLE_CVM_FETCH")!="1":
        raise RuntimeError("CVM network collection is disabled")
    validate_cvm_document(url)
    filename=urlparse(url).path.rsplit("/",1)[-1]
    raw=fetcher(url)
    result=ingest_bytes(workspace_id=workspace_id,company_id=company_id,
         filename=filename,content=raw,source_url=url,publisher="CVM",
         document_version=document_version)
    return {**result,"source_url":url,"source_verified":False,
            "note":"Downloaded from allowlisted address; contents require source and accounting verification."}
