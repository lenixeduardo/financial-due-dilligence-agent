# DFP/ITR ZIP extraction — offline parser

The official CVM data portal publishes annual DFP and ITR ZIP datasets. `parse_cvm_archive` accepts supplied bytes, never fetches an arbitrary URL and never extracts files to disk.

Selection requires CVM company code, exercise year and dataset kind. It parses BPA/BPP/DRE/DFC consolidated and standalone CSV files, filters by `CD_CVM` and `ORDEM_EXERC=ÚLTIMO`, and stores raw scale/amount and version in typed AccountingLine objects.

Safety bounds: archive 32 MiB, 100 members, 120 MiB total expanded size, 45 MiB per member, 300,000 rows per CSV, no nested filenames or encrypted members. Validates accounting number finiteness. Large datasets can exceed these limits and must be processed by a separate streaming/sandboxed job.

**Not yet a verified indicator pipeline**: no mapping of account codes to sector-specific financial ratios, no restatement resolution, no annual versus quarterly period reconciliation, and no automatic matching of issuer legal identity. A local ZIP is untrusted until its hash and provenance are confirmed from CVM.

The project intentionally keeps ZIP parsing separate from network access; the CVM fetch endpoint remains disabled by default.
