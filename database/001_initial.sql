BEGIN;
CREATE TABLE IF NOT EXISTS workspaces (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence (
 id TEXT PRIMARY KEY,
 workspace_id TEXT NOT NULL REFERENCES workspaces(id),
 company_id TEXT NOT NULL,
 source_url TEXT NOT NULL CHECK (source_url LIKE 'https://%'),
 publisher TEXT NOT NULL,
 document_version TEXT NOT NULL,
 page INTEGER NOT NULL CHECK (page > 0),
 content_sha256 CHAR(64) NOT NULL,
 text_content TEXT NOT NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS evidence_workspace_company_idx ON evidence(workspace_id,company_id);
COMMIT;
