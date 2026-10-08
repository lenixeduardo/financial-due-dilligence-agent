import json
from app.db import initialize_database, ensure_workspace, insert_evidence, list_evidence, connection
from app.evidence import Evidence
from app.retrieval_db import search_chunks
from app.hybrid import hybrid_search, VECTOR_DIM

def test_sqlite_roundtrip_and_tenant_scope(tmp_path, monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH", str(tmp_path / "data.sqlite3"))
    initialize_database()
    for w in ("one", "two"):
        ensure_workspace(w)
        item = Evidence.create(id=w, workspace_id=w, company_id="apple",
            source_url="https://www.gov.br/cvm", publisher="CVM",
            document_version="v1", page=1, text="revenue cash flow")
        insert_evidence(item)
        with connection() as db:
            db.execute("INSERT INTO evidence_chunks(id,evidence_id,workspace_id,company_id,page,chunk_order,body) VALUES(?,?,?,?,?,?,?)",
                       (w+"-chunk",w,w,"apple",1,0,"revenue cash flow"))
            db.execute("INSERT INTO chunk_embeddings(chunk_id,workspace_id,model_id,embedding_json) VALUES(?,?,?,?)",
                       (w+"-chunk",w,"test",json.dumps([1.0]+[0.0]*383)))
    assert [e.id for e in list_evidence("one", "apple")] == ["one"]
    assert [c.chunk_id for c in search_chunks(workspace_id="one",company_id="apple",query="cash")] == ["one-chunk"]
    hits=hybrid_search(workspace_id="one",company_id="apple",query="cash",
        embedding=[1.0]+[0.0]*383,model_id="test")
    assert [h.chunk_id for h in hits] == ["one-chunk"]
    initialize_database()
