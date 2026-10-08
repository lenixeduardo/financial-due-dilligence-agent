# Production acceptance gates — NOT YET APPROVED

The existence of a passing CI build is not sufficient to claim a release is production-ready. The project is not yet at 100%.

## Engineering
- [x] Backend, frontend and SQLite automated test workflows.
- [x] Container-build CI.
- [x] Local identity, scoped bearer sessions, roles and separate reviewer permission.
- [x] SQLite consistent backup/restore with integrity tests.
- [x] Basic DFP calculation source hashes and version-conflict refusal.
- [ ] Automated security dependency and penetration testing; remediate findings.
- [ ] Production login and role workflow tested through real HTTPS end-to-end.
- [ ] User provisioning, revocation, disk permissions and incident response validated.
- [ ] Periodic off-host encrypted backups enabled, restore drill timed and recovery objective documented.
- [ ] External CVM network fetching through egress-protected infrastructure; verify live official files.
- [ ] Real DFP/ITR accounting reconciliation, restatement/version policy and sectoral formula review.
- [ ] Verified semantic embedding/indexing + LLM evaluation on cited financial documents.
- [ ] Data retention, LGPD/legal assessment, source licensing and privacy documentation.
- [ ] Monitoring, alerting, log privacy, resource/capacity and load testing.
- [ ] Host, domain, DNS, TLS and durable volumes provisioned; staging acceptance signoff.

**Decision:** BLOCKED. This file describes the blockers; it must not be toggled to approved by code alone. A responsible human operator must demonstrate the external controls and approve a documented acceptance test.

SQLite is a single-host architecture. Do not deploy the backend on ephemeral serverless storage.
