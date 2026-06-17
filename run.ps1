# CursorOS Electron Quick Launcher
$ProjectRoot = Get-Location
$ElectronPath = Join-Path $ProjectRoot "cursoros-electron"

if (Test-Path (Join-Path $ElectronPath "node_modules\electron\cli.js")) {
    Write-Host "Launching CursorOS Electron..." -ForegroundColor Cyan
    Set-Location $ElectronPath
    npx electron .
} else {
    Write-Host "Error: Electron not found. Run 'npm install' in cursoros-electron/ first." -ForegroundColor Red
}
