# =====================================================================
#  build_appliance.ps1 - Freeze the Ask ABUZ8 MCP server with PyInstaller
#  and assemble dist-appliance\Ask-ABUZ8-Portable\ : exe + console + sample
#  ledger + launcher, ready to zip onto a USB stick (house pattern from
#  ABUZ8_PORTABLE: build script + run launcher + sanitized payload).
#  Usage:  powershell -ExecutionPolicy Bypass -File appliance\build_appliance.ps1
# =====================================================================
param(
  [string]$Out = (Join-Path $PSScriptRoot '..\dist-appliance\Ask-ABUZ8-Portable')
)
$ErrorActionPreference = 'Stop'
function Say($m){ Write-Host "[build] $m" }
$Repo = Split-Path $PSScriptRoot -Parent

# 1. Dedicated build venv (the dev .venv stays byte-identical to requirements.txt)
$BuildVenv = Join-Path $PSScriptRoot '.build-venv'
$BVPy = Join-Path $BuildVenv 'Scripts\python.exe'
if(-not (Test-Path $BVPy)){
  # Prefer the dev venv's interpreter (same base, always works), then PATH python.
  # NOTE: bare `py` is deliberately NOT used — its default can point at a
  # missing interpreter (seen: ghost 3.14) while `python` works fine.
  $DevPy = Join-Path $Repo '.venv\Scripts\python.exe'
  $created = $false
  foreach($cand in @($DevPy, 'python')){
    if(Test-Path $BuildVenv){ Remove-Item $BuildVenv -Recurse -Force -EA SilentlyContinue }
    if(($cand -like '*\*') -and -not (Test-Path $cand)){ continue }
    if(($cand -notlike '*\*') -and -not (Get-Command $cand -EA SilentlyContinue)){ continue }
    try { & $cand -m venv $BuildVenv 2>$null } catch { }
    if(Test-Path $BVPy){ $created = $true; Say "build venv created via $cand"; break }
  }
  if(-not $created){ throw 'could not create build venv (tried dev-venv python, then python)' }
}
Say "installing pinned deps + pyinstaller into build venv..."
& $BVPy -m pip install -q -r (Join-Path $Repo 'requirements.txt')
& $BVPy -m pip install -q pyinstaller==6.22.3
$PI = Join-Path $BuildVenv 'Scripts\pyinstaller.exe'
Say "pyinstaller $(& $PI --version)"

# 2. Freeze (one-dir; data stays external by design — see the .spec)
Push-Location $Repo
try {
  & $PI appliance/Ask-ABUZ8.spec --distpath dist-appliance --workpath build-appliance --clean --noconfirm
} finally { Pop-Location }
$Frozen = Join-Path $Repo 'dist-appliance\Ask-ABUZ8'
if(-not (Test-Path (Join-Path $Frozen 'Ask-ABUZ8.exe'))){ throw 'freeze produced no exe' }

# 3. Assemble the portable folder
if(Test-Path $Out){ Remove-Item $Out -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Out | Out-Null
Copy-Item (Join-Path $Frozen 'Ask-ABUZ8.exe') $Out -Force
Copy-Item (Join-Path $Frozen '_internal') $Out -Recurse -Force
Copy-Item (Join-Path $Repo 'simulator') $Out -Recurse -Force
New-Item -ItemType Directory -Force -Path (Join-Path $Out 'data') | Out-Null
Copy-Item (Join-Path $Repo 'data\feed.json') (Join-Path $Out 'data\feed.json') -Force
New-Item -ItemType Directory -Force -Path (Join-Path $Out 'config') | Out-Null
Copy-Item (Join-Path $PSScriptRoot 'feed.txt') (Join-Path $Out 'config\feed.txt') -Force
Copy-Item (Join-Path $PSScriptRoot 'Start-Ask-ABUZ8.bat') $Out -Force
Copy-Item (Join-Path $PSScriptRoot 'README.md') $Out -Force

# 4. Sanitize (no dev residue, no decisions, pristine seed only)
Get-ChildItem $Out -Recurse -Include __pycache__,*.pyc,*.log,feed.runtime.json -EA SilentlyContinue |
  Remove-Item -Recurse -Force -EA SilentlyContinue

# 5. Zip + hash (zip keeps the top-level folder: unzip → double-click)
$Zip = Join-Path $Repo 'dist-appliance\Ask-ABUZ8-Portable-win64.zip'
if(Test-Path $Zip){ Remove-Item $Zip -Force }
Compress-Archive -Path $Out -DestinationPath $Zip
$Hash = (Get-FileHash $Zip -Algorithm SHA256).Hash
"$Hash  Ask-ABUZ8-Portable-win64.zip" | Set-Content (Join-Path $Repo 'dist-appliance\Ask-ABUZ8-Portable-win64.zip.sha256') -NoNewline

$mb = "{0:N1} MB" -f ((Get-Item $Zip).Length/1MB)
Say "DONE. Appliance folder : $Out"
Say "DONE. Zip for release : $Zip ($mb)"
Say "DONE. SHA-256         : $Hash"
Say "Next: extract the zip on a machine without Python and double-click Start-Ask-ABUZ8.bat."
