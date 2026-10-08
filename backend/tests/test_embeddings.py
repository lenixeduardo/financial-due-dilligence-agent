from app.db import initialize_database,ensure_workspace,connection
from app.evidence import Evidence
from app.ingestion import ingest_bytes
from app.embeddings import index_embeddings
from app.hybrid import hybrid_search,VECTOR_DIM

def test_local_embedding_adapter_and_idempotent_index(tmp_path,monkeypatch):
    monkeypatch.setenv("FINSIGHT_SQLITE_PATH",str(tmp_path/"db.sqlite"))
    initialize_database()
    ensure_workspace("w")
    ingest_bytes(workspace_id="w",company_id="firm",filename="data.txt",content=b"Operating cash flow improved",
                 publisher="Issuer",document_version="v1",source_url="https://example.org/data")
    def encoder(texts):
        return [[1.0]+[0.0]*(VECTOR_DIM-1) for _ in texts]
    assert index_embeddings(workspace_id="w",company_id="firm",model_id="test",encoder=encoder)==1
    assert index_embeddings(workspace_id="w",company_id="firm",model_id="test",encoder=encoder)==0
    hits=hybrid_search(workspace_id="w",company_id="firm",query="cash",
        embedding=[1.0]+[0.0]*(VECTOR_DIM-1),model_id="test")
    assert len(hits)==1
