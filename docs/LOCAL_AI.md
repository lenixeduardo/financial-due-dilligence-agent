# Optional local AI configuration (no Supabase required)

Embeddings: install `pip install sentence-transformers` into the Python environment and pre-download a **trusted, licensed 384-dimensional sentence-transformers model** into a local directory. Then call `local_sentence_transformer_encoder(model_path)` and `index_embeddings(..., encoder=...)`. The core installation does NOT download models or silently call external endpoints.

Interpretation: optionally run an Ollama model locally on loopback port 11434. `draft_interpretation` passes bounded excerpts, uses structured JSON mode, verifies workspace/company citation membership and exact quote text, and always returns **requires_human_review** rather than certifying claims. No automatic financial ratio calculation is delegated to an LLM.

Current limitations: no commercial data feed, no reviewer approval UI, no complete semantic-entailment verifier, and no guarantee of prompt-injection robustness. Treat all model drafts as untrusted until manually reviewed. Large or hostile PDFs require isolated parsing.
