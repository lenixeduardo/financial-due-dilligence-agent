import pytest
from fastapi import HTTPException
from app.evidence import Evidence, retrieve, support_claim
from app.access import authorize_workspace

def example(workspace="w1", company="apple", ident="1"):
    return Evidence.create(id=ident,workspace_id=workspace,company_id=company,
        source_url="https://example.org/report.pdf",publisher="IR",document_version="v1",
        page=2,text="revenue and cash flow")

def test_retrieval_isolated_by_workspace_and_company():
    records=[example(),example("w2",ident="2"),example(company="other",ident="3")]
    assert [e.id for e in retrieve("revenue",workspace_id="w1",company_id="apple",documents=records)]==["1"]

def test_citation_is_not_equated_with_verified_claim():
    finding=support_claim("Revenue increased",["1"],workspace_id="w1",company_id="apple",documents=[example()])
    assert finding.status=="requires_verification"

def test_foreign_citation_rejected():
    finding=support_claim("Revenue increased",["2"],workspace_id="w1",company_id="apple",documents=[example("w2",ident="2")])
    assert finding.status=="unsupported"

def test_no_key_fails_closed(monkeypatch):
    monkeypatch.delenv("FINSIGHT_WORKSPACE_API_KEY",raising=False)
    with pytest.raises(HTTPException):
        authorize_workspace("w1", "password")

def test_non_https_rejected():
    with pytest.raises(ValueError):
        Evidence.create(id="x",workspace_id="w",company_id="c",source_url="http://example.org",
                        publisher="issuer",document_version="v1",page=1,text="data")
