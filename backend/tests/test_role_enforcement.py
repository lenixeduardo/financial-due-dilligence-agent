"""Role checks for SQLite bearer sessions and immutable reviewer attribution."""
from fastapi.testclient import TestClient
from app.main import app
from app.db import initialize_database,ensure_workspace
from app.user_auth import create_user,authenticate

def seed(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"roles.sqlite"))
    monkeypatch.setenv("FINSIGHT_AUTH_MODE","users")
    monkeypatch.setenv("FINSIGHT_ENV","production")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    initialize_database()
    ensure_workspace("local")
    create_user(workspace_id="local",username="read_user",password="reader-test-password-123",role="reader")
    create_user(workspace_id="local",username="analyst_user",password="analyst-test-password-123",role="analyst")
    create_user(workspace_id="local",username="reviewer_user",password="reviewer-test-password-123",role="reviewer")
    def token(username,password):
        return {"Authorization":"Bearer "+authenticate(workspace_id="local",username=username,password=password)}
    return token("read_user","reader-test-password-123"),token("analyst_user","analyst-test-password-123"),token("reviewer_user","reviewer-test-password-123")

def test_read_and_write_permissions(tmp_path,monkeypatch):
    read,analyst,reviewer=seed(tmp_path,monkeypatch)
    evidence={"id":"test-doc","company_id":"firm","source_url":"https://www.gov.br/cvm/example",
       "publisher":"CVM","document_version":"2025","page":1,"text":"Cash flow"}
    with TestClient(app) as client:
        url="/v1/workspaces/local/evidence"
        assert client.post(url,json=evidence,headers=read).status_code==403
        assert client.post(url,json=evidence,headers=reviewer).status_code==403
        assert client.post(url,json=evidence,headers=analyst).status_code==201
        assert client.post("/v1/workspaces/foreign/evidence",json=evidence,headers=analyst).status_code==403
        assert client.post(url,json=evidence,headers={"X-Workspace-Key":"obsolete-shared-key"}).status_code==401

def test_reviewer_attribution_is_server_owned(tmp_path,monkeypatch):
    from app.cvm_indicators import CalculatedIndicator
    from app.indicator_store import persist_indicators
    from decimal import Decimal
    read,analyst,reviewer=seed(tmp_path,monkeypatch)
    persist_indicators("local",[CalculatedIndicator(metric_code="net_margin",company_code="1234",
       period="2025-12-31",scope="consolidated",value=Decimal("0.10"),unit="ratio",
       formula_version="cvm-basic-v1",source_sha256="a"*64,account_codes=("3.11","3.01"))])
    payload={"company_code":"1234","period":"2025-12-31","scope":"consolidated",
        "metric_code":"net_margin","formula_version":"cvm-basic-v1","dataset_sha256":"a"*64,
        "decision":"approved","reviewer":"forged_admin",
        "justification":"Cross-checked all disclosed accounting statements."}
    with TestClient(app) as client:
        url="/v1/workspaces/local/cvm/indicators/reviews"
        assert client.post(url,json=payload,headers=analyst).status_code==403
        result=client.post(url,json=payload,headers=reviewer)
        assert result.status_code==201,result.text
        history=client.get("/v1/workspaces/local/cvm/1234/reviews",headers=read)
        assert history.status_code==200
        assert history.json()["events"][0]["reviewer"]=="reviewer_user"
