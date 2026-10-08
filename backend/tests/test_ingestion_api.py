import base64
from fastapi.testclient import TestClient
from app.main import app

def test_protected_document_pipeline(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"api.sqlite"))
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","demo")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","secret-test-token")
    headers={"X-Workspace-Key":"secret-test-token"}
    payload={"company_id":"cvm","filename":"report.txt",
             "base64_content":base64.b64encode(b"Revenue growth 2025").decode(),
             "source_url":"https://www.gov.br/cvm/report","publisher":"CVM","document_version":"2025"}
    with TestClient(app) as client:
        assert client.post("/v1/workspaces/demo/documents/ingest",json=payload).status_code==403
        # Authentication header required.
        stored=client.post("/v1/workspaces/demo/documents/ingest",json=payload,headers=headers)
        assert stored.status_code==200,stored.text
        answer=client.post("/v1/workspaces/demo/analysis/evidence",
            json={"company_id":"cvm","question":"Revenue"},headers=headers)
        assert answer.status_code==200,answer.text
        assert answer.json()["status"]=="evidence_found_requires_review"
        assert answer.json()["interpretation"] is None
        assert client.post("/v1/workspaces/foreign/analysis/evidence",
           json={"company_id":"cvm","question":"Revenue"},headers=headers).status_code==403
