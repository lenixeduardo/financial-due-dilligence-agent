from fastapi.testclient import TestClient
from app.main import app
from app import evidence_api

client = TestClient(app)
def test_evidence_fails_closed_without_key(monkeypatch):
    monkeypatch.delenv("FINSIGHT_WORKSPACE_API_KEY",raising=False)
    response=client.post("/v1/workspaces/demo/evidence/search",json={"company_id":"apple","query":"revenue"})
    assert response.status_code == 403

def test_wrong_workspace_rejected(monkeypatch):
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","secret-testing-only")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","workspace-one")
    response=client.post("/v1/workspaces/workspace-two/evidence/search",headers={"X-Workspace-Key":"secret-testing-only"},
       json={"company_id":"apple","query":"revenue"})
    assert response.status_code == 403

def test_scoped_search(monkeypatch):
    from app.evidence import Evidence
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","secret-testing-only")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","workspace-one")
    monkeypatch.setattr(evidence_api,"list_evidence",lambda workspace,company,limit: [
      Evidence.create(id="a",workspace_id="workspace-one",company_id="apple",
      source_url="https://example.com/a",publisher="Issuer",document_version="1",page=1,text="revenue cash"),
      Evidence.create(id="b",workspace_id="foreign",company_id="apple",
      source_url="https://example.com/b",publisher="Issuer",document_version="1",page=1,text="revenue cash")
    ])
    response=client.post("/v1/workspaces/workspace-one/evidence/search",headers={"X-Workspace-Key":"secret-testing-only"},
       json={"company_id":"apple","query":"revenue"})
    assert response.status_code == 200
    assert [e["id"] for e in response.json()["evidence"]]==["a"]
