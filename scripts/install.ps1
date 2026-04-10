# Donghua CLI Windows Installer
# Installs via pip and sets up PowerShell aliases

Write-Host ""
Write-Host "  ╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║       Donghua CLI Installer          ║" -ForegroundColor Cyan
Write-Host "  ║   武侠动画终端 · v3.1.0              ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Detect Python
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    Write-Host "  X Python not found." -ForegroundColor Red
    Write-Host "  Install from https://www.python.org/ or run: winget install Python.Python.3.12"
    exit 1
}

$pyVer = & $pythonCmd --version 2>&1
Write-Host "  + Found $pyVer" -ForegroundColor Green

# Install via pip
Write-Host ""
Write-Host "  Installing donghua-cli..." -ForegroundColor Yellow
& $pythonCmd -m pip install donghua-cli --quiet
Write-Host "  + Installed" -ForegroundColor Green

# Check for mpv
Write-Host ""
if (Get-Command mpv -ErrorAction SilentlyContinue) {
    Write-Host "  + mpv found" -ForegroundColor Green
} elseif (Get-Command vlc -ErrorAction SilentlyContinue) {
    Write-Host "  + vlc found (mpv recommended)" -ForegroundColor Yellow
} else {
    Write-Host "  ! No video player found." -ForegroundColor Yellow
    Write-Host "  Install mpv: winget install mpv" -ForegroundColor Gray
    Write-Host "  Or download from https://mpv.io/" -ForegroundColor Gray
}

# Add PowerShell aliases
$profilePath = $PROFILE.CurrentUserCurrentHost
if (-not $profilePath) { $profilePath = $PROFILE }
$profileDir = Split-Path $profilePath
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}

$currentContent = Get-Content $profilePath -ErrorAction SilentlyContinue
if (-not ($currentContent -match "Donghua CLI")) {
    $aliasBlock = @"

# Donghua CLI Aliases
function dhua { donghua `$args }
function dhua360 { donghua --quality 360 `$args }
function dhua480 { donghua --quality 480 `$args }
function dhua720 { donghua --quality 720 `$args }
function dhua1080 { donghua --quality 1080 `$args }
function dhuadl { donghua --download `$args }
"@
    Add-Content -Path $profilePath -Value $aliasBlock
    Write-Host ""
    Write-Host "  + Aliases added to $profilePath" -ForegroundColor Green
} else {
    Write-Host "  + Aliases already configured" -ForegroundColor Gray
}

Write-Host ""
Write-Host "  ══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "    + Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "    Usage:" -ForegroundColor White
Write-Host "      dhua                    # interactive" -ForegroundColor Gray
Write-Host "      donghua 'Soul Land'     # direct search" -ForegroundColor Gray
Write-Host "      dhua --tui              # full-screen TUI" -ForegroundColor Gray
Write-Host "      dhuadl 'Soul Land'      # download" -ForegroundColor Gray
Write-Host ""
Write-Host "    Restart PowerShell or run: . `$PROFILE" -ForegroundColor Yellow
Write-Host "  ══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
