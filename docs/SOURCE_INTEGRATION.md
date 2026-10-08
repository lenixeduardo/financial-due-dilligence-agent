# Official source integration, phase 1

Allowlisted source fetcher is an internal library; not exposed as a user-controlled URL API.

- `download_official` bounds response bytes and time, rejects redirects and proxies, and checks public DNS answers.
- **Not sufficient on its own against DNS rebinding / TOCTOU**: deployment must enforce egress firewall/proxy with destination-IP checks at connection time.
- The allowlist is deliberately restrictive and must be expanded only after confirming endpoints, licensing and usage policies.
- Do not assume a fetched document is authentic; validate issuer, expected path, metadata, hash, media type and accounting dates before indexing.
- Do not use this module to automatically ingest PDFs as RAG; ingestion parsing, file sandbox, pgvector and citations remain separate pending work.
- Never submit confidential financial files to arbitrary LLM providers.

Acceptance before activation: blocked private-network tests, controlled egress deployment, legal/licensing review, bounded parser, checksum, trace logs without sensitive payloads.
