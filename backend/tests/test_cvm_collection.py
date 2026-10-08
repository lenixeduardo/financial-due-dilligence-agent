import pytest
from app.cvm_collection import collect_cvm_document,validate_cvm_document
from app.db import initialize_database,ensure_workspace,list_evidence

CVM_URL="https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/company.csv"

@pytest.mark.parametrize("url",[
    "https://dados.cvm.gov.br.evil.invalid/dados/CIA_ABERTA/CAD/DADOS/doc.csv",
    "https://dados.cvm.gov.br/dados/other/doc.csv",
    "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/doc.zip",
    "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/doc.csv?redirect=1",
    "http://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/doc.csv",
])
def test_invalid_source_rejected(url):
    with pytest.raises(ValueError):
        validate_cvm_document(url)

def test_collection_disabled_by_default(monkeypatch):
    monkeypatch.delenv("FINSIGHT_ENABLE_CVM_FETCH",raising=False)
    with pytest.raises(RuntimeError):
        collect_cvm_document(workspace_id="local",company_id="demo",
            url=CVM_URL,document_version="2025",fetcher=lambda _:b"revenue")

def test_collection_with_stubbed_network(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"db.sqlite3"))
    monkeypatch.setenv("FINSIGHT_ENABLE_CVM_FETCH","1")
    initialize_database()
    ensure_workspace("local")
    calls=[]
    def fake_fetch(url):
        calls.append(url)
        return b"COMPANY;REVENUE\nDEMO;500\n"
    output=collect_cvm_document(workspace_id="local",company_id="demo",
        url=CVM_URL,document_version="2025",fetcher=fake_fetch)
    assert calls==[CVM_URL]
    assert output["source_verified"] is False
    assert output["new_chunks"]==1
    assert list_evidence("local","demo")[0].publisher=="CVM"
