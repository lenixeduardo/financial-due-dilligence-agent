"""Hybrid FTS/vector retrieval over verified chunks.

Vectors must be supplied by a separately versioned trusted embedding model.
Never uses LLM-generated document claims as a retrieval source.
"""
from math import isfinite
from typing import Sequence
from pydantic import BaseModel
from .db import connection

VECTOR_DIM=384

class Hit(BaseModel):
    chunk_id:str
    evidence_id:str
    publisher:str
    source_url:str
    page:int
    snippet:str
    score:float

def validate_embedding(vector:Sequence[float])->str:
    if len(vector)!=VECTOR_DIM or any(not isfinite(float(x)) for x in vector):
        raise ValueError("expected 384 finite embedding values")
    return "[" + ",".join(str(float(x)) for x in vector) + "]"

def hybrid_search(*,workspace_id:str,company_id:str,query:str,embedding:Sequence[float],
                  model_id:str,limit:int=10)->list[Hit]:
    if not workspace_id or not company_id or not model_id or not query.strip() or len(query)>500 or not 1<=limit<=20:
        raise ValueError("invalid search parameters")
    encoded=validate_embedding(embedding)
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
             SELECT c.id as chunk_id,c.evidence_id,e.publisher,e.source_url,c.page,
                left(c.body,1600) as snippet,
                (0.40*ts_rank(c.text_search,websearch_to_tsquery('simple',%s))+
                 0.60*(1 - (v.embedding <=> %s::vector)))::float8 as score
             FROM evidence_chunks c
             JOIN evidence e ON e.id=c.evidence_id AND e.workspace_id=c.workspace_id AND e.company_id=c.company_id
             JOIN chunk_embeddings v ON v.chunk_id=c.id AND v.workspace_id=c.workspace_id AND v.model_id=%s
             WHERE c.workspace_id=%s AND c.company_id=%s
             ORDER BY score DESC,c.id LIMIT %s
            """,(query,encoded,model_id,workspace_id,company_id,limit))
            rows=cursor.fetchall()
    return [Hit(**row) for row in rows]
