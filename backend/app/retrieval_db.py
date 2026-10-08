"""SQLite FTS5 retrieval with workspace and company isolation."""
from pydantic import BaseModel
from .db import connection

class RetrievedChunk(BaseModel):
    chunk_id: str
    evidence_id: str
    source_url: str
    publisher: str
    page: int
    snippet: str
    rank: float

def search_chunks(*, workspace_id: str, company_id: str, query: str, limit: int = 10) -> list[RetrievedChunk]:
    if not workspace_id or not company_id or not query.strip() or len(query)>500 or not 1<=limit<=20:
        raise ValueError("invalid scoped search")
    # Quote every whitespace-delimited token; never interpret raw user input as FTS syntax.
    tokens = [t.replace('"','') for t in query.split() if t.replace('"','')]
    if not tokens:
        return []
    match = " OR ".join('"' + token + '"' for token in tokens[:30])
    with connection() as conn:
        rows = conn.execute("""
          SELECT c.id AS chunk_id,c.evidence_id,e.source_url,e.publisher,c.page,
                 substr(c.body,1,1600) AS snippet, -bm25(evidence_fts) AS rank
          FROM evidence_fts
          JOIN evidence_chunks c ON c.rowid=evidence_fts.rowid
          JOIN evidence e ON e.id=c.evidence_id AND e.workspace_id=c.workspace_id AND e.company_id=c.company_id
          WHERE c.workspace_id=? AND c.company_id=? AND evidence_fts MATCH ?
          ORDER BY rank DESC,c.id LIMIT ?""",(workspace_id,company_id,match,limit)).fetchall()
    return [RetrievedChunk(**dict(r)) for r in rows]
