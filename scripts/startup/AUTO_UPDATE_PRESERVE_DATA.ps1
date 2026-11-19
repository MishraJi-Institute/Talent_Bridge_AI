$ErrorActionPreference = "Stop"
$Destination = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$LogDir = Join-Path $Destination "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir "auto-update.log"
$Marker = Join-Path $Destination ".talentbridge_auto_update_done"
function Log($Message) { Add-Content -Path $Log -Value ("[{0}] {1}" -f (Get-Date -Format s), $Message) -Encoding UTF8 }
if (Test-Path $Marker) { Log "One-time data-preserving update already completed; skipping."; exit 0 }
# Prior folder seen in the user's earlier VS Code screenshot. Can be overridden without editing this file.
$Candidates = @()
if ($env:TALENTBRIDGEAI_OLD_ROOT) { $Candidates += $env:TALENTBRIDGEAI_OLD_ROOT }
$Candidates += @("E:\Job Portal 15 Nov 2026 4 pm\TalentBridgeAI", (Join-Path (Split-Path $Destination -Parent) "TalentBridgeAI"))
$Source = $null
foreach ($candidate in ($Candidates | Select-Object -Unique)) {
    if ([string]::IsNullOrWhiteSpace($candidate)) { continue }
    if ((Test-Path (Join-Path $candidate "backend\legacy-django\manage.py")) -and ((Resolve-Path $candidate).Path -ne $Destination)) { $Source = (Resolve-Path $candidate).Path; break }
}
if (-not $Source) {
    Log "No previous checkout found automatically. No files changed. Set TALENTBRIDGEAI_OLD_ROOT if old data must be imported."
    exit 0
}
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Backup = Join-Path $Destination "backups\auto_update_$stamp"
New-Item -ItemType Directory -Force -Path $Backup | Out-Null
$Copied = @()
foreach ($name in @(".env", "database", "private_media", "media", "uploads")) {
    $from = Join-Path $Source $name
    $to = Join-Path $Destination $name
    if (-not (Test-Path $from)) { continue }
    # Preserve destination data if it already exists; backup it, then merge source files without deleting anything.
    if (Test-Path $to) { Copy-Item $to -Destination (Join-Path $Backup $name) -Recurse -Force }
    if ((Get-Item $from).PSIsContainer) {
        New-Item -ItemType Directory -Force -Path $to | Out-Null
        & robocopy.exe $from $to /E /COPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS | Out-Null
        if ($LASTEXITCODE -ge 8) { throw "Copy failed for $name; see $Log" }
    } else {
        if (-not (Test-Path $to)) { Copy-Item $from $to -Force }
    }
    $Copied += $name
}
Set-Content -Path $Marker -Value ("Completed {0}; source={1}; copied={2}; backup={3}" -f (Get-Date -Format s), $Source, ($Copied -join ','), $Backup) -Encoding UTF8
Log "Data-preserving first-open update complete. Source=$Source; copied=$($Copied -join ','); backup=$Backup"
