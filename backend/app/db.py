"""Local SQLite persistence for FinSight. No Supabase/PostgreSQL required."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .evidence import Evidence

SCHEMA = """
CREATE TABLE IF NOT EXISTS workspaces (
 id TEXT PRIMARY KEY, name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evidence (
 id TEXT PRIMARY KEY,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 company_id TEXT NOT NULL,
 source_url TEXT NOT NULL CHECK(source_url LIKE 'https://%'),
 publisher TEXT NOT NULL,
 document_version TEXT NOT NULL,
 page INTEGER NOT NULL CHECK(page > 0),
 content_sha256 TEXT NOT NULL,
 text_content TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS evidence_workspace_company_idx
 ON evidence(workspace_id,company_id,created_at DESC);
CREATE TABLE IF NOT EXISTS evidence_chunks (
 id TEXT PRIMARY KEY,
 evidence_id TEXT NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 company_id TEXT NOT NULL,
 page INTEGER NOT NULL CHECK(page > 0),
 chunk_order INTEGER NOT NULL CHECK(chunk_order >= 0),
 body TEXT NOT NULL CHECK(length(body)>0),
 UNIQUE(evidence_id,chunk_order)
);
CREATE INDEX IF NOT EXISTS chunks_scope ON evidence_chunks(workspace_id,company_id);
CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts USING fts5(body, content='evidence_chunks', content_rowid='rowid');
CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON evidence_chunks BEGIN
 INSERT INTO evidence_fts(rowid,body) VALUES(new.rowid,new.body);
END;
CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON evidence_chunks BEGIN
 INSERT INTO evidence_fts(evidence_fts,rowid,body) VALUES('delete',old.rowid,old.body);
END;
CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON evidence_chunks BEGIN
 INSERT INTO evidence_fts(evidence_fts,rowid,body) VALUES('delete',old.rowid,old.body);
 INSERT INTO evidence_fts(rowid,body) VALUES(new.rowid,new.body);
END;
CREATE TABLE IF NOT EXISTS chunk_embeddings (
 chunk_id TEXT NOT NULL REFERENCES evidence_chunks(id) ON DELETE CASCADE,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 model_id TEXT NOT NULL,
 embedding_json TEXT NOT NULL,
 indexed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(chunk_id,model_id)
);
CREATE INDEX IF NOT EXISTS chunk_embeddings_scope ON chunk_embeddings(workspace_id,model_id);
"""

def _database_path() -> Path:
    value = os.environ.get("FINSIGHT_SQLITE_PATH", "data/finsight.sqlite3")
    if value == ":memory:":
        raise ValueError("Use a file-backed SQLite database to preserve evidence across connections")
    path = Path(value).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

@contextmanager
def connection():
    conn = sqlite3.connect(str(_database_path()), timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=10000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database():
    with connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)

def ensure_workspace(workspace_id: str):
    if not workspace_id:
        raise ValueError("workspace required")
    with connection() as conn:
        conn.execute("INSERT OR IGNORE INTO workspaces(id,name) VALUES(?,?)", (workspace_id,workspace_id))

def insert_evidence(e: Evidence) -> None:
    with connection() as conn:
        if conn.execute("SELECT 1 FROM evidence WHERE id=?", (e.id,)).fetchone():
            raise ValueError("duplicate evidence identifier")
        conn.execute(
            """INSERT INTO evidence(id,workspace_id,company_id,source_url,publisher,
            document_version,page,content_sha256,text_content)
            VALUES(?,?,?,?,?,?,?,?,?)""",
            (e.id,e.workspace_id,e.company_id,e.source_url,e.publisher,
             e.document_version,e.page,e.sha256_hex,e.text))

def list_evidence(workspace_id: str, company_id: str, limit: int = 25) -> list[Evidence]:
    if not 1 <= limit <= 100:
        raise ValueError("invalid limit")
    with connection() as conn:
        rows = conn.execute(
            """SELECT * FROM evidence WHERE workspace_id=? AND company_id=?
            ORDER BY created_at DESC,id LIMIT ?""",(workspace_id,company_id,limit)).fetchall()
    return [Evidence(id=r["id"],workspace_id=r["workspace_id"],company_id=r["company_id"],
      source_url=r["source_url"],publisher=r["publisher"],document_version=r["document_version"],
      page=r["page"],text=r["text_content"],sha256_hex=r["content_sha256"]) for r in rows]
