# Deployment — not ready for public access

1. Provision a private PostgreSQL instance and distinct least-privilege database role.
2. Apply `database/001_initial.sql` and `database/002_evidence_tenant_uniqueness.sql` once in order.
3. Configure `FINSIGHT_DATABASE_URL`, `FINSIGHT_WORKSPACE_ID`, `FINSIGHT_WORKSPACE_API_KEY` using managed secrets.
4. Keep the application behind private network access and HTTPS reverse proxy.
5. Verify health, authentication-denial, workspace isolation and backup restore.
6. **Before public release** replace shared workspace key with user identity provider + server-side RBAC and DB RLS.
7. Do not ingest sensitive documents until retention/privacy controls and audit logging are completed.

These scripts were committed but not applied to a running database. There is no managed PostgreSQL instance linked to this repository.
