BEGIN;
-- A document identifier cannot be silently reused across workspaces.
ALTER TABLE evidence ADD CONSTRAINT evidence_workspace_id_unique UNIQUE (workspace_id,id);
CREATE INDEX IF NOT EXISTS evidence_tenant_latest_idx ON evidence(workspace_id,company_id,created_at DESC);
COMMIT;
