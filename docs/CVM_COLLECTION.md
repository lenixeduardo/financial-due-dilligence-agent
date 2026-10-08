# CVM collection (opt-in, local only)

This step adds protected, explicit collection of PDF, TXT and CSV from narrow official CVM document paths under https://dados.cvm.gov.br/. The endpoint is **disabled by default**. The server downloads from the allowed URL, checks size through the existing downloader, and indexes extracted text in local SQLite.

Set `FINSIGHT_ENABLE_CVM_FETCH=1` ONLY when network access is restricted by a trusted egress firewall or proxy that blocks DNS rebinding and internal IP connections. Existing DNS preflight checks do not themselves prevent DNS TOCTOU. Leave disabled until egress isolation is established.

Known boundaries: most CVM structured DFP/ITR datasets are ZIP archives; this phase intentionally does **not** unpack ZIP or reconcile financial metrics. No B3 or IR connector is represented as complete. The API accepts only predefined document areas, and results are marked unverified. Confirm actual URLs, licensing, content authenticity, CSV delimiter and encoding before use in finance.

Tests stub remote HTTP and exercise URL rejection, default-disabled behavior, and SQLite indexing. They do NOT confirm live availability of the example document.
