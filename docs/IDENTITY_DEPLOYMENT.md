# Identity and permissions for single-host FinSight

Use this mode for any deployment outside an isolated local development environment.

Set `FINSIGHT_ENV=production` and `FINSIGHT_AUTH_MODE=users` on the API process. Build the frontend with `VITE_FINSIGHT_AUTH_MODE=users`. Never expose the shared-key development mode to the public internet.

Provision a persistent, private SQLite path, initialize the DB and provision accounts from the server's trusted command line:

```sh
export FINSIGHT_SQLITE_PATH=/srv/finsight-private/finsight.sqlite3
export FINSIGHT_ENV=production
export FINSIGHT_AUTH_MODE=users
export FINSIGHT_WORKSPACE_ID=local
PYTHONPATH=backend python -c "from app.db import initialize_database,ensure_workspace;initialize_database();ensure_workspace('local')"
python -m backend.scripts.create_user --workspace local --username administrator --role admin
```

The provisioning command prompts for a password rather than taking it from shell history. Roles: reader (read), analyst (ingestion/calculations), reviewer (manual reviews), admin (all). No public signup endpoint.

The API issues random, hashed-on-disk bearer tokens, expires sessions after eight hours, supports revocation, rate-limits failed usernames and uses scrypt password hashes. The frontend holds tokens in memory only (a page refresh requires a new login). Serve API and UI on the same HTTPS origin behind an authenticated reverse proxy. Secure filesystem permissions, backups, HTTPS, log redaction, session revocation upon account deactivation and monitoring remain deployment responsibilities.

**Production acceptance is not yet granted**: no deployment infrastructure, penetration test, load test, full supply-chain audit, consent/privacy review or verified CVM accounting dataset is in place. The existing CVM ingestion may not be enabled without egress firewall safeguards. Do not claim 100% production readiness on the basis of these auth changes alone.
