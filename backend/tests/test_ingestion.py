import pytest
from app.db import initialize_database,ensure_workspace,connection
from app.ingestion import ingest_bytes,extract_pages,chunk_text
from app.analysis import answer_from_evidence

@pytest.fixture
def local_db(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"finsight.db"))
    initialize_database()
    ensure_workspace("finance")
    ensure_workspace("other")

def test_text_ingestion_search_and_replay(local_db):
    kwargs=dict(workspace_id="finance", company_id="firm-a",filename="filing.txt",
        content=b"Revenue increased in the reporting period. Operating cash flow was positive.",
        source_url="https://www.gov.br/cvm/filing",publisher="CVM",document_version="2025-FY")
    r=ingest_bytes(**kwargs)
    assert r["new_chunks"]==1
    assert ingest_bytes(**kwargs)["new_chunks"]==0
    result=answer_from_evidence(workspace_id="finance",company_id="firm-a",question="Revenue")
    assert result.status=="evidence_found_requires_review"
    assert result.passages[0]["page"]==1
    assert answer_from_evidence(workspace_id="other",company_id="firm-a",question="Revenue").status=="insufficient_evidence"

def test_unsupported_or_spoofed_files(local_db):
    with pytest.raises(ValueError):
        extract_pages("bad.pdf",b"not a pdf")
    with pytest.raises(ValueError):
        extract_pages("bad.exe",b"arbitrary bytes")
    with pytest.raises(ValueError):
        extract_pages("huge.txt",b"a"*(8*1024*1024+1))

def test_rollback_for_bad_metadata(local_db):
    with pytest.raises(ValueError):
        ingest_bytes(workspace_id="finance",company_id="firm-a",filename="report.txt",
            content=b"cash",source_url="http://unsafe.example",publisher="Issuer",document_version="v1")
    with connection() as conn:
        assert conn.execute("SELECT count(*) FROM evidence").fetchone()[0]==0

def test_chunk_overlap():
    assert len(chunk_text("x"*1400))==2
