"""Optional on-device embedding pipeline. No model is downloaded automatically."""
import json
from typing import Callable, Sequence
from .db import connection
from .hybrid import VECTOR_DIM, validate_embedding

def index_embeddings(*, workspace_id: str, company_id: str, model_id: str,
                     encoder: Callable[[list[str]], Sequence[Sequence[float]]],
                     batch_size: int = 16) -> int:
    if not workspace_id or not company_id or not model_id or not 1 <= batch_size <= 64:
        raise ValueError("invalid embedding job parameters")
    with connection() as conn:
        rows=conn.execute("""SELECT c.id,c.body FROM evidence_chunks c
           LEFT JOIN chunk_embeddings v ON v.chunk_id=c.id AND v.model_id=?
           WHERE c.workspace_id=? AND c.company_id=? AND v.chunk_id IS NULL
           ORDER BY c.id LIMIT 5000""",(model_id,workspace_id,company_id)).fetchall()
    completed=0
    for i in range(0,len(rows),batch_size):
        batch=rows[i:i+batch_size]
        vectors=encoder([r["body"] for r in batch])
        if len(vectors)!=len(batch):
            raise ValueError("embedding adapter returned wrong number of vectors")
        validated=[validate_embedding(v) for v in vectors]
        with connection() as conn:
            for row,encoded in zip(batch,validated):
                conn.execute("""INSERT OR IGNORE INTO chunk_embeddings(chunk_id,workspace_id,model_id,embedding_json)
                   VALUES(?,?,?,?)""",(row["id"],workspace_id,model_id,encoded))
        completed+=len(batch)
    return completed

def local_sentence_transformer_encoder(model_path: str):
    """Requires optional sentence-transformers and a pre-installed local model."""
    from pathlib import Path
    path=Path(model_path)
    if not path.is_dir():
        raise ValueError("local embedding model path not found")
    from sentence_transformers import SentenceTransformer
    model=SentenceTransformer(str(path),local_files_only=True)
    if model.get_sentence_embedding_dimension()!=VECTOR_DIM:
        raise ValueError("local model must output 384-dimension vectors")
    def encode(texts: list[str]):
        return model.encode(texts,normalize_embeddings=True).tolist()
    return encode
