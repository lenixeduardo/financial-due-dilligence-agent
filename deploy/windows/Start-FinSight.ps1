# Run with PowerShell under the same Windows user who installed the application.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Base = Join-Path $env:LOCALAPPDATA "FinSight"
$Db = Join-Path $Base "data\finsight.sqlite3"
$Backups = Join-Path $Base "backups"
if (-not (Test-Path $Python)) { throw "Run Install-FinSight.ps1 first." }
if (-not (Test-Path (Join-Path $Root "frontend\dist\index.html"))) { throw "Frontend build missing. Run the installer." }
New-Item -ItemType Directory -Force -Path (Split-Path $Db), $Backups | Out-Null
$env:FINSIGHT_ENV = "production"
$env:FINSIGHT_AUTH_MODE = "users"
$env:FINSIGHT_SQLITE_PATH = $Db
$env:FINSIGHT_BACKUP_DIR = $Backups
$env:FINSIGHT_WORKSPACE_ID = "local"
$env:FINSIGHT_FRONTEND_DIST = (Join-Path $Root "frontend\dist")
$env:FINSIGHT_LOCAL_PORT = "8765"
$env:PYTHONPATH = (Join-Path $Root "backend")
Push-Location $Root
try { & $Python -m scripts.windows_serve; if ($LASTEXITCODE -ne 0) { throw "FinSight startup failed: $LASTEXITCODE" } }
finally { Pop-Location }
