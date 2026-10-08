# Single-host deployment candidate — requires operational homologation

This is a Docker Compose + Caddy configuration for a **dedicated Linux host with durable disk**, not Vercel serverless.

Prerequisites:
- Dedicated VM, domain with DNS pointing at the host, firewall ports 80/443, outbound Internet for ACME certificate issuance.
- Create a private durable directory, e.g. `/srv/finsight-data`, owned by uid/gid 10001 and not inside the web root.
- Add a local environment file containing `FINSIGHT_DATA_PATH=/srv/finsight-data`, `FINSIGHT_WORKSPACE_ID=local`, and `FINSIGHT_DOMAIN=finance.example.com`. Replace with your own domain and do not commit private settings.
- Docker Compose v2, ongoing patching, log aggregation, monitoring and encrypted off-host backups.
- Keep CVM outbound collection disabled until a trusted egress filtering solution is deployed.

Start:
`docker compose --env-file .env.production -f compose.production.yml up -d --build`

Provision the initial admin locally after the database initializes:
`docker compose --env-file .env.production -f compose.production.yml exec api python -c "from app.db import ensure_workspace;ensure_workspace('local')"`

**The container runs as an unprivileged user**. Provision accounts through the private server terminal, not an HTTP endpoint:
`docker compose --env-file .env.production -f compose.production.yml exec -it api python -m scripts.create_user --workspace local --username administrator --role admin`
The command interactively prompts for a password. Do not permit self-registration or store initial passwords in environment variables.

Known release blockers: account provisioning needs an operational runbook, frontend/backend end-to-end testing on real HTTPS, dynamic security scanning, external disk backup automation, financial reconciliation with actual CVM filings, source licensing and privacy retention review.

Production readiness is NOT guaranteed by the presence of Docker and HTTPS configuration.
