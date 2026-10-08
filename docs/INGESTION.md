# Local ingestion pipeline

The ingestion library accepts only explicit application-provided bytes of PDF, UTF-8 TXT, or CSV; it does not fetch untrusted URLs or expose a public upload route. It enforces an 8 MB input limit, a 100-page PDF limit, and a per-page character bound. Scanned PDFs require a separate review/OCR pipeline.

Each indexed page carries publisher, URL, document version, page, source file SHA-256 and text SHA-256. Chunk records are linked to their source evidence and indexed by SQLite FTS5.

`answer_from_evidence` retrieves passages but deliberately **does not generate an AI interpretation**. It returns `insufficient_evidence` or `evidence_found_requires_review`. A matching passage is not proof that a claim is true.

Production blockers: robust sandbox for hostile PDFs, ingestion endpoint RBAC, document authenticity validation, source licenses, semantic embedding model, evaluation dataset and human review.
