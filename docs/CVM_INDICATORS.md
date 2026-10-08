# Initial CVM deterministic indicators

The conservative `cvm-basic-v1` methodology maps basic CVM statement codes:
- DRE 3.01 net revenue, 3.05 operating result, 3.11 net income.
- BPA 1.01 current assets, BPP 2.01 current liabilities.
- Operating margin, net margin, current ratio from compatible lines.

Requirements: exactly one company, reference date, scope, DFP file hash and reporting version; duplicate account codes rejected. Missing/zero denominator -> indicator omitted. CSV `UNIDADE` and `MIL` values are normalized by Decimal prior to division. Results are stored in SQLite with formula version, codes and source ZIP hash; they remain `requires_source_review` until independently matched to official filings.

**Known limitations:** DFP only; ITR cumulative quarterly calculations need a different treatment. The mapping is a starting point subject to issuer/accounting review; companies may define account extensions and restate filings. No unattended scoring, financial advice or verified-source status is generated.
