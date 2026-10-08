# Per-user Windows 10/11 installer; requires Python 3.12 and Node.js 22.
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Push-Location $Root
try {
  if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw "Python launcher (py) is required. Install Python 3.12." }
  if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw "Node.js / npm is required. Install Node.js 22 LTS." }
  & py -3.12 -m venv .venv
  if ($LASTEXITCODE -ne 0) { throw "Python virtual environment creation failed." }
  $Python = Join-Path $Root ".venv\Scripts\python.exe"
  & $Python -m pip install -r backend\requirements.txt
  if ($LASTEXITCODE -ne 0) { throw "Python dependencies failed." }
  Push-Location frontend
  try {
    & npm.cmd ci
    if ($LASTEXITCODE -ne 0) { throw "npm install failed." }
    $env:VITE_FINSIGHT_AUTH_MODE = "users"
    & npm.cmd run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
  } finally { Pop-Location }
  $Base = Join-Path $env:LOCALAPPDATA "FinSight"
  New-Item -ItemType Directory -Force -Path (Join-Path $Base "data"),(Join-Path $Base "backups") | Out-Null
  $env:FINSIGHT_SQLITE_PATH = (Join-Path $Base "data\finsight.sqlite3")
  $env:PYTHONPATH = (Join-Path $Root "backend")
  & $Python -c "from app.db import initialize_database,ensure_workspace; initialize_database();ensure_workspace('local')"
  if ($LASTEXITCODE -ne 0) { throw "Database initialization failed." }
  Write-Host "Create an administrator account. Password input is hidden."
  & $Python -m scripts.create_user --workspace local --username administrator --role admin
  if ($LASTEXITCODE -ne 0) { throw "Administrator provisioning failed." }
  $Launcher = Join-Path $PSScriptRoot "Start-FinSight.ps1"
  $Startup = [Environment]::GetFolderPath("Startup")
  $Shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $Startup "FinSight.lnk"))
  $Shortcut.TargetPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
  $Shortcut.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + $Launcher + '"'
  $Shortcut.WorkingDirectory = $Root
  $Shortcut.Description = "FinSight local server at http://127.0.0.1:8765"
  $Shortcut.Save()
  Write-Host "Installed. Start with .\deploy\windows\Start-FinSight.ps1; open http://127.0.0.1:8765"
  Write-Host "Startup shortcut installed for this Windows user. Database is stored in $Base."
} finally { Pop-Location }
