BEGIN;
CREATE TABLE IF NOT EXISTS evidence_chunks (
 id TEXT PRIMARY KEY,
 evidence_id TEXT NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 company_id TEXT NOT NULL,
 page INTEGER NOT NULL CHECK(page>0),
 chunk_order INTEGER NOT NULL CHECK(chunk_order>=0),
 body TEXT NOT NULL CHECK(length(body)>0),
 text_search tsvector GENERATED ALWAYS AS (to_tsvector('simple',body)) STORED,
 UNIQUE(evidence_id,chunk_order)
);
CREATE INDEX IF NOT EXISTS chunks_scope ON evidence_chunks(workspace_id,company_id);
CREATE INDEX IF NOT EXISTS chunks_fts ON evidence_chunks USING gin(text_search);
COMMIT;
