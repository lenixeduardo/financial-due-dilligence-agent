"""Append-only manual review decisions for versioned CVM financial indicators."""
from hashlib import sha256
import json
import re
from .db import connection
from .indicator_store import SCHEMA as INDICATORS_SCHEMA

REVIEW_SCHEMA="""
CREATE TABLE IF NOT EXISTS indicator_reviews (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 company_code TEXT NOT NULL,
 period TEXT NOT NULL,
 scope TEXT NOT NULL,
 metric_code TEXT NOT NULL,
 formula_version TEXT NOT NULL,
 dataset_sha256 TEXT NOT NULL,
 decision TEXT NOT NULL CHECK(decision IN ('approved','rejected')),
 reviewer TEXT NOT NULL,
 justification TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 prev_hash TEXT NOT NULL,
 event_hash TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS indicator_review_lookup
 ON indicator_reviews(workspace_id,company_code,period,scope,metric_code,formula_version,dataset_sha256,id);
CREATE TRIGGER IF NOT EXISTS indicator_reviews_no_update BEFORE UPDATE ON indicator_reviews
 BEGIN SELECT RAISE(ABORT,'review history is append-only'); END;
CREATE TRIGGER IF NOT EXISTS indicator_reviews_no_delete BEFORE DELETE ON indicator_reviews
 BEGIN SELECT RAISE(ABORT,'review history is append-only'); END;
"""
def review_indicator(*,workspace_id:str,company_code:str,period:str,scope:str,metric_code:str,
                     formula_version:str,dataset_sha256:str,decision:str,reviewer:str,justification:str)->dict:
    if decision not in ("approved","rejected") or not re.fullmatch(r"[a-zA-Z0-9_.@-]{3,100}",reviewer):
        raise ValueError("invalid decision or reviewer identifier")
    if not (15<=len(justification.strip())<=2000):
        raise ValueError("review justification must contain 15–2000 characters")
    key=(workspace_id,company_code,period,scope,metric_code,formula_version,dataset_sha256)
    with connection() as db:
        db.executescript(INDICATORS_SCHEMA+REVIEW_SCHEMA)
        db.execute("BEGIN IMMEDIATE")
        exists=db.execute("""SELECT 1 FROM calculated_indicators WHERE workspace_id=? AND company_code=?
            AND period=? AND scope=? AND metric_code=? AND formula_version=? AND dataset_sha256=?""",key).fetchone()
        if not exists:
            raise ValueError("indicator not found in this workspace or version")
        last=db.execute("SELECT event_hash FROM indicator_reviews ORDER BY id DESC LIMIT 1").fetchone()
        prev=last["event_hash"] if last else "GENESIS"
        payload=json.dumps({"key":key,"decision":decision,"reviewer":reviewer,
                            "justification":justification.strip(),"prev":prev},sort_keys=True)
        digest=sha256(payload.encode()).hexdigest()
        cursor=db.execute("""INSERT INTO indicator_reviews
          (workspace_id,company_code,period,scope,metric_code,formula_version,dataset_sha256,
           decision,reviewer,justification,prev_hash,event_hash)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(*key,decision,reviewer,justification.strip(),prev,digest))
        result={"event_id":cursor.lastrowid,"decision":decision,"reviewer":reviewer,
                "event_hash":digest,"status":"manual_review_recorded"}
    return result

def list_reviews(workspace_id:str,company_code:str)->list[dict]:
    with connection() as db:
        db.executescript(INDICATORS_SCHEMA+REVIEW_SCHEMA)
        rows=db.execute("""SELECT id,period,scope,metric_code,formula_version,dataset_sha256,
          decision,reviewer,justification,created_at,prev_hash,event_hash
          FROM indicator_reviews WHERE workspace_id=? AND company_code=? ORDER BY id DESC""",
          (workspace_id,company_code)).fetchall()
    return [dict(row) for row in rows]
