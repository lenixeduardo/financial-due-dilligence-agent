"""PostgreSQL evidence repository; all queries are parameterized and workspace scoped."""
import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from .evidence import Evidence

@contextmanager
def connection():
    dsn = os.environ.get("FINSIGHT_DATABASE_URL")
    if not dsn:
        raise RuntimeError("FINSIGHT_DATABASE_URL is not configured")
    with psycopg.connect(dsn, row_factory=dict_row, connect_timeout=5) as conn:
        yield conn

def insert_evidence(e: Evidence) -> None:
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO evidence(id,workspace_id,company_id,source_url,publisher,
                   document_version,page,content_sha256,text_content)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING""",
                (e.id,e.workspace_id,e.company_id,e.source_url,e.publisher,e.document_version,
                 e.page,e.sha256_hex,e.text))
        conn.commit()

def list_evidence(workspace_id: str, company_id: str, limit: int = 25) -> list[Evidence]:
    if not 1 <= limit <= 100:
        raise ValueError("invalid limit")
    with connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT id,workspace_id,company_id,source_url,publisher,document_version,page,
                   content_sha256,text_content FROM evidence WHERE workspace_id=%s AND company_id=%s
                   ORDER BY created_at DESC,id LIMIT %s""",
                (workspace_id, company_id, limit))
            rows = cursor.fetchall()
    return [Evidence(id=r["id"],workspace_id=r["workspace_id"],company_id=r["company_id"],
             source_url=r["source_url"],publisher=r["publisher"],document_version=r["document_version"],
             page=r["page"],text=r["text_content"],sha256_hex=r["content_sha256"]) for r in rows]
