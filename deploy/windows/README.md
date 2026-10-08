# FinSight on Windows 10/11

Designed for a **single Windows computer and a single logged-in Windows user**. This is a local installation, not an internet-facing production deployment. Python 3.12, Node.js 22 LTS, PowerShell 5.1+ and a checked-out repository are prerequisites. No Docker or Supabase needed.

In Windows PowerShell, from the repository root:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy\windows\Install-FinSight.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\deploy\windows\Start-FinSight.ps1
```
The installer installs dependencies, builds the frontend with login enabled, initializes the SQLite file under `%LOCALAPPDATA%\FinSight\data`, prompts interactively for an administrator password, and adds a per-user Startup shortcut. At login, FinSight runs on **http://127.0.0.1:8765**, never binds to a LAN or public interface. A Windows restart will require the user to log in before Startup executes.

The background backup worker creates integrity-checked SQLite snapshots every 6 hours at `%LOCALAPPDATA%\FinSight\backups` and retains up to 14. Backups on the same disk are **not** disaster recovery: regularly export an encrypted off-machine backup and verify a restoration. Use Windows disk encryption and restrict the Windows account.

A Windows Firewall inbound rule is not needed for loopback-only listening. To stop the service, close its PowerShell window. Uninstall the Startup shortcut at `shell:startup` before removing files. Do not delete the data directory unless intentionally wiping the data.

**Windows acceptance tests on the target PC remain mandatory**: dependency installation, initial login, DFP import, review permissions, backup/restore, reboot, endpoint binding and antivirus/firewall compatibility. This installer does not establish public TLS, offsite backup, full financial-data verification or a completed security audit. Keep the app local until those checks have been completed.
