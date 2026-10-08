"""Accounting integrity gates for scope and restatements in a DFP ZIP."""
from io import BytesIO
from zipfile import ZipFile
from fastapi.testclient import TestClient
from app.main import app

HEADER="CD_CVM;DT_REFER;CD_CONTA;DS_CONTA;VL_CONTA;ORDEM_EXERC;ESCALA_MOEDA;VERSAO\n"
def dfp_zip(rows):
    output=BytesIO()
    with ZipFile(output,"w") as archive:
        for scope,version,revenue,profit in rows:
            data=HEADER+f"1234;2025-12-31;3.01;Receita;{revenue};ÚLTIMO;MIL;{version}\n"
            data+=f"1234;2025-12-31;3.05;Resultado;{profit};ÚLTIMO;MIL;{version}\n"
            archive.writestr(f"dfp_cia_aberta_DRE_{scope}_2025.csv",data.encode())
    import base64
    return base64.b64encode(output.getvalue()).decode()

def setup(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"test.sqlite"))
    monkeypatch.setenv("FINSIGHT_WORKSPACE_ID","local")
    monkeypatch.setenv("FINSIGHT_WORKSPACE_API_KEY","testing-only-secret")
    return {"X-Workspace-Key":"testing-only-secret"}

def test_scopes_never_combined(tmp_path,monkeypatch):
    headers=setup(tmp_path,monkeypatch)
    payload={"company_code":"1234","year":2025,
             "zip_base64":dfp_zip([("con","1","200","40"),("ind","1","100","10")])}
    with TestClient(app) as client:
        response=client.post("/v1/workspaces/local/cvm/dfp/indicators",json=payload,headers=headers)
    assert response.status_code==200,response.text
    margins=[(i["scope"],i["value"]) for i in response.json()["computed"] if i["metric_code"]=="operating_margin"]
    assert sorted(margins)==[("consolidated","0.2"),("standalone","0.1")]

def test_conflicting_restatements_rejected(tmp_path,monkeypatch):
    headers=setup(tmp_path,monkeypatch)
    # Same document rows with different reported versions:
    output=BytesIO()
    with ZipFile(output,"w") as archive:
        data=HEADER+"1234;2025-12-31;3.01;Receita;200;ÚLTIMO;MIL;1\n"
        data+="1234;2025-12-31;3.05;Resultado;40;ÚLTIMO;MIL;2\n"
        archive.writestr("dfp_cia_aberta_DRE_con_2025.csv",data.encode())
    import base64
    payload={"company_code":"1234","year":2025,"zip_base64":base64.b64encode(output.getvalue()).decode()}
    with TestClient(app) as client:
        response=client.post("/v1/workspaces/local/cvm/dfp/indicators",json=payload,headers=headers)
    assert response.status_code==422
    assert "restatements" in response.json()["detail"]
