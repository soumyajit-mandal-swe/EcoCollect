$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$runtimeDir = Join-Path $PSScriptRoot '.runtime'
New-Item -ItemType Directory -Force $runtimeDir | Out-Null
$pythonExe = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (!(Test-Path $pythonExe)) { throw 'Python environment missing. Follow README.md setup instructions first.' }
if (!(Test-Path '.env')) { throw 'Missing .env. Copy .env.example and configure your MySQL credentials.' }
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if (!$nodeCommand) {
    $bundledNode = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe'
    if (Test-Path $bundledNode) { $nodeExe = $bundledNode } else { throw 'Node.js is missing. Install Node.js LTS, then reopen PowerShell.' }
} else { $nodeExe = $nodeCommand.Source }
if (!(Test-Path 'frontend\node_modules\vite\bin\vite.js')) { throw 'Frontend packages missing. Run npm install in frontend first.' }
# Uses the installed MySQL84 service; no bundled server is launched.
$ready = $false
for ($attempt=0; $attempt -lt 20; $attempt++) {
    & $pythonExe -m backend.check_db
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Milliseconds 500
}
if (!$ready) { throw 'MySQL is unavailable. Start MySQL and check DB_HOST, DB_PORT, DB_USER and DB_PASSWORD in .env. See .runtime logs.' }
if (!(Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $pythonExe -ArgumentList '-m uvicorn backend.main:app --host 127.0.0.1 --port 8001' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput "$runtimeDir\backend.log" -RedirectStandardError "$runtimeDir\backend-error.log"
}
if (!(Get-NetTCPConnection -LocalPort 5174 -State Listen -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath $nodeExe -ArgumentList 'node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5174' -WorkingDirectory (Join-Path $PSScriptRoot 'frontend') -WindowStyle Hidden -RedirectStandardOutput "$runtimeDir\frontend.log" -RedirectStandardError "$runtimeDir\frontend-error.log"
}
for ($attempt=0; $attempt -lt 20; $attempt++) {
    try {
        $health = Invoke-RestMethod 'http://127.0.0.1:8001/api/health'
        $page = Invoke-WebRequest 'http://127.0.0.1:5174' -UseBasicParsing
        if ($health.database -eq 'MySQL' -and $page.StatusCode -eq 200) { Write-Host 'EcoCollect is ready: http://127.0.0.1:5174'; exit 0 }
    } catch { Start-Sleep -Milliseconds 500 }
}
throw 'A server did not start. Check .runtime/backend-error.log and .runtime/frontend-error.log, and ensure ports 8001 and 5174 are free.'
