# Indicator manual review (local)

Every decision records reviewer identifier, approval/rejection, justification, source ZIP hash, formula version and accounting scope in an append-only SQLite table. Review history is not overwritten by subsequent decisions; hash linkage makes accidental mutation more detectable.

This is a review-event record, **not proof of reviewer identity**. The present shared workspace key is not user authentication; never represent reviewer-submitted names as identity-verified. Formal approval workflows require login/RBAC, reviewer independence, accounting document verification and stronger tamper-evident audit storage.

Different ZIP hashes remain separate calculated indicator versions. No automatic restatement winner or verified/latest accounting conclusion is selected.
