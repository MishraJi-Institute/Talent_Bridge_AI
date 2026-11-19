$ErrorActionPreference = "Stop"
$Destination = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$DefaultSource = "E:\Job Portal 15 Nov 2026 4 pm\TalentBridgeAI"

Write-Host "TalentBridgeAI safe update: code will be updated while your data is preserved." -ForegroundColor Cyan
if (Test-Path (Join-Path $DefaultSource "backend\legacy-django\manage.py")) {
    $Source = $DefaultSource
} else {
    $Source = Read-Host "Enter the FULL path of your CURRENT TalentBridgeAI project folder"
}
if (!(Test-Path (Join-Path $Source "backend\legacy-django\manage.py"))) {
    throw "Source project not found or backend\legacy-django\manage.py missing: $Source"
}
$Source = (Resolve-Path $Source).Path
if ($Source -eq $Destination) {
    Write-Host "Source and destination are the same folder. Existing data will be kept in place." -ForegroundColor Yellow
} else {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backup = Join-Path $Destination "backups\before_data_preserving_update_$stamp"
    New-Item -ItemType Directory -Force -Path $backup | Out-Null

    foreach ($name in @(".env", "database", "private_media", "media", "uploads")) {
        $destItem = Join-Path $Destination $name
        if (Test-Path $destItem) {
            Copy-Item $destItem -Destination $backup -Recurse -Force
        }
    }

    foreach ($name in @(".env", "database", "private_media", "media", "uploads")) {
        $sourceItem = Join-Path $Source $name
        if (!(Test-Path $sourceItem)) { continue }
        $destItem = Join-Path $Destination $name
        if ((Get-Item $sourceItem).PSIsContainer) {
            New-Item -ItemType Directory -Force -Path $destItem | Out-Null
            & robocopy.exe $sourceItem $destItem /E /COPY:DAT /R:2 /W:1 /NFL /NDL /NJH /NJS
            if ($LASTEXITCODE -ge 8) { throw "Data copy failed for $name (robocopy exit $LASTEXITCODE)." }
        } else {
            Copy-Item $sourceItem -Destination $destItem -Force
        }
    }
    Write-Host "Existing .env, database and uploads copied. Backup: $backup" -ForegroundColor Green
}

Write-Host "Installing checks, Windows sign-in auto-start and starting the server..." -ForegroundColor Cyan
& (Join-Path $Destination "INSTALL_TALENTBRIDGEAI.bat")
if ($LASTEXITCODE -ne 0) { throw "TalentBridgeAI installer failed. Review logs\setup.log and logs\server.log." }
