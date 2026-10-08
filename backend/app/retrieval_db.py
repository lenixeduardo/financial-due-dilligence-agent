"""Real PostgreSQL full-text retrieval, always scoped to workspace and company.

Future vector re-ranking is not represented as operational until embeddings exist.
"""
from pydantic import BaseModel,Field
from .db import connection

class RetrievedChunk(BaseModel):
    chunk_id:str
    evidence_id:str
    source_url:str
    publisher:str
    page:int
    snippet:str
    rank:float

def search_chunks(*,workspace_id:str,company_id:str,query:str,limit:int=10)->list[RetrievedChunk]:
    if not workspace_id or not company_id or not query.strip() or len(query)>500 or not 1<=limit<=20:
        raise ValueError("invalid scoped search")
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
              SELECT c.id as chunk_id,c.evidence_id,e.source_url,e.publisher,c.page,
                 left(c.body,1600) as snippet,
                 ts_rank(c.text_search,websearch_to_tsquery('simple',%s)) as rank
              FROM evidence_chunks c
              JOIN evidence e ON e.id=c.evidence_id AND e.workspace_id=c.workspace_id
                 AND e.company_id=c.company_id
              WHERE c.workspace_id=%s AND c.company_id=%s
                AND c.text_search @@ websearch_to_tsquery('simple',%s)
              ORDER BY rank DESC,c.id LIMIT %s
            """,(query,workspace_id,company_id,query,limit))
            rows=cursor.fetchall()
    return [RetrievedChunk(**row) for row in rows]
