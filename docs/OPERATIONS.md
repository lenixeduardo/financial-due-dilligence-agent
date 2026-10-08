# SQLite operational recovery

FinSight uses a **single persistent disk** and is not suitable for serverless ephemeral filesystems without an external durable storage strategy.

Backup from an application process with exclusive filesystem permission:
`PYTHONPATH=backend python -c "from app.backup import backup_database; print(backup_database('/secure/backups/finsight-backup.sqlite'))"`

Verify:
`PYTHONPATH=backend python -c "from app.backup import verify_backup; print(verify_backup('/secure/backups/finsight-backup.sqlite'))"`

Restore only while the application is stopped, and **to a new path**:
`PYTHONPATH=backend python -c "from app.backup import restore_database; print(restore_database('/secure/backups/finsight-backup.sqlite','/secure/restore/finsight.sqlite'))"`

Do not place backups in public, static or Git directories. Encrypt backups at rest using infrastructure-level keys. Test recovery and define recovery point/recovery time objectives before operating with real customer data. WAL snapshots made by raw file copy can be inconsistent; use the SQLite backup API above.

Before declaring the application production-ready, implement full user identity/RBAC, private host/network hardening, external egress protection for official-source downloads, authentic CVM data reconciliation, regulatory/privacy retention review, monitoring and an audited restore drill.
