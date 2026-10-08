from fastapi.testclient import TestClient
from app.main import app

def metric(company,sector,metric="operating_margin"):
    return {"company_id":company,"sector":sector,"metric":metric,"period":"2025-FY",
            "value":"12.5","source_ids":["document-1"],"formula_version":"v1"}

def test_valid_sector_comparison_with_explicit_unverified_status(monkeypatch):
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","test-secret")
    with TestClient(app) as client:
        response=client.post("/v1/workspaces/local/comparisons/validate",headers={"X-Workspace-Key":"test-secret"},
                             json={"observations":[metric("a","retail"),metric("b","retail")]})
        assert response.status_code==200,response.text
        assert response.json()["ranked"] is False
        assert response.json()["evidence_status"]=="unverified_user_submitted"
        denied=client.post("/v1/workspaces/foreign/comparisons/validate",headers={"X-Workspace-Key":"test-secret"},
                           json={"observations":[metric("a","retail"),metric("b","retail")]})
        assert denied.status_code==403

def test_bad_sector_metric_blocked(monkeypatch):
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","test-secret")
    with TestClient(app) as client:
        response=client.post("/v1/workspaces/local/comparisons/validate",headers={"X-Workspace-Key":"test-secret"},
                json={"observations":[metric("a","bank","net_debt_ebitda"),metric("b","bank","net_debt_ebitda")]})
        assert response.status_code==422
