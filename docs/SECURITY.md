# Security and completion gates

## Current boundary
Prototype, **not production-ready**. There is no auth, uploads, web crawler, RAG, report exporter or confidential document storage. The API must not be exposed on a public network before authentication, request quotas and deployment hardening.

## Required before production
- Authentication and per-workspace authorization; tenant isolation in database and vector search.
- Structured provenance: source URL, retrieval time, publisher, document version, page, snippet and file hash.
- SSRF-safe fetcher with allowlisted hosts, DNS/IP checks on every redirect, disabled cloud metadata access and egress firewall.
- Untrusted-document processing with file signatures, size limits, sandbox, time limits and malware checking.
- Prompt injection tests; retrieved text is data, never instructions; no model authority over tools.
- Input constraints, audit logs, secrets handling, backup/restore, retention and privacy review.
- Verification of formula baselines and financial sector-specific standards; prohibit non-comparable ranking.
- Provenance checking of LLM factual assertions; unsupported conclusions must be withheld.
- CVM/B3/RI integration license and terms-of-use review, LGPD assessment.
- Dependency and secret scanning, penetration testing, access control tests and end-to-end acceptance suite.

## Financial rules
Use Decimal. Reject missing/mismatched periods, currencies, consolidation scope, zero denominators and non-finite numbers. Formula versions and evidence IDs are first-class output fields. No ranking is returned from cross-sector comparison.

## Known gaps
The current application is only a deterministic API foundation. No security warranty or claim of production readiness.
