"""SQLite hybrid text + vector retrieval; bounded Python cosine scoring for small local datasets."""
import json
from math import isfinite, sqrt
from typing import Sequence
from pydantic import BaseModel
from .db import connection
from .retrieval_db import search_chunks

VECTOR_DIM=384
class Hit(BaseModel):
    chunk_id: str
    evidence_id: str
    publisher: str
    source_url: str
    page: int
    snippet: str
    score: float

def validate_embedding(vector: Sequence[float]) -> str:
    if len(vector)!=VECTOR_DIM or any(not isfinite(float(x)) for x in vector):
        raise ValueError("expected 384 finite embedding values")
    return json.dumps([float(x) for x in vector])

def cosine(a:Sequence[float],b:Sequence[float]) -> float:
    na=sqrt(sum(v*v for v in a)); nb=sqrt(sum(v*v for v in b))
    if na==0 or nb==0:
        return 0.0
    return sum(x*y for x,y in zip(a,b))/(na*nb)

def hybrid_search(*,workspace_id:str,company_id:str,query:str,embedding:Sequence[float],
                  model_id:str,limit:int=10)->list[Hit]:
    if not workspace_id or not company_id or not model_id or not query.strip() or len(query)>500 or not 1<=limit<=20:
        raise ValueError("invalid search parameters")
    validate_embedding(embedding)
    lexical={hit.chunk_id:hit.rank for hit in search_chunks(workspace_id=workspace_id,company_id=company_id,query=query,limit=20)}
    with connection() as conn:
        rows=conn.execute("""
        SELECT c.id AS chunk_id,c.evidence_id,e.publisher,e.source_url,c.page,
          substr(c.body,1,1600) AS snippet,v.embedding_json
        FROM chunk_embeddings v
        JOIN evidence_chunks c ON c.id=v.chunk_id AND c.workspace_id=v.workspace_id
        JOIN evidence e ON e.id=c.evidence_id AND e.workspace_id=c.workspace_id AND e.company_id=c.company_id
        WHERE v.workspace_id=? AND c.company_id=? AND v.model_id=?
        LIMIT 5000""",(workspace_id,company_id,model_id)).fetchall()
    max_lex=max([abs(v) for v in lexical.values()] or [1.0]) or 1.0
    output=[]
    for row in rows:
        vector=json.loads(row["embedding_json"])
        if len(vector)!=VECTOR_DIM:
            continue
        similarity=(cosine(embedding,vector)+1)/2
        score=0.6*similarity+0.4*max(0,lexical.get(row["chunk_id"],0))/max_lex
        output.append(Hit(chunk_id=row["chunk_id"],evidence_id=row["evidence_id"],
            publisher=row["publisher"],source_url=row["source_url"],page=row["page"],
            snippet=row["snippet"],score=score))
    return sorted(output,key=lambda x:(-x.score,x.chunk_id))[:limit]
