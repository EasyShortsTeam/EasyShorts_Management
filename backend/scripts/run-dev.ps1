$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here '..')
Set-Location $root

if (!(Test-Path .\.venv)) {
  python -m venv .venv
}

. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# load .env if exists
if (Test-Path .\.env) {
  Get-Content .\.env | ForEach-Object {
    if ($_ -match '^\s*#') { return }
    if ($_ -match '^\s*$') { return }
    $pair = $_.Split('=',2)
    if ($pair.Length -eq 2) {
      [System.Environment]::SetEnvironmentVariable($pair[0].Trim(), $pair[1].Trim())
    }
  }
}

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
