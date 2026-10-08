# DFP dossier workbench (local)

Individual analysis now includes a CVM DFP ZIP import and indicator-view panel.

1. Start the SQLite-backed backend on 127.0.0.1 with FINSIGHT_WORKSPACE_ID and FINSIGHT_WORKSPACE_API_KEY configured.
2. Start the Vite frontend; use the individual-analysis tab and DFP dossier section.
3. Enter workspace, local API key, numeric CVM code and exercise year, then provide an authorized official DFP ZIP.
4. The API filters the ZIP for eligible company/year entries and calculates initial deterministic indicators.
5. The UI displays the value, period, scope, formula/version, account codes and source ZIP SHA-256.
6. Export a JSON research draft with explicit not-reviewed status. The export is client-side and is NOT a certified financial report.

Limitations: This is not an automatic real-source authenticity check. Mapped DRE/BPA/BPP codes need accounting validation, and newer restatements and quarterly ITR are not resolved. No reviewer approval action is available yet. The data provided is not published to a hosted service. Do not treat calculated values as investment advice or audit opinions.
