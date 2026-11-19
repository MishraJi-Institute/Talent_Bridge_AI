$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$source = Join-Path $root "js\demo-forms.js"
if (-not (Test-Path $source)) {
    throw "Cannot find js\demo-forms.js. Run this script from the TalentBridgeAI project."
}

$content = [System.IO.File]::ReadAllText($source)
if ($content -match "You are viewing the static preview") {
    $backup = "$source.before-banner-fix.bak"
    if (-not (Test-Path $backup)) {
        Copy-Item $source $backup
    }

    $functionPattern = '(?s)\s*function showBackendNotice\(\)\s*\{.*?\r?\n  \}\r?\n'
    $content2 = [regex]::Replace(
        $content,
        $functionPattern,
        "`r`n  // Static-preview warning banner intentionally removed.`r`n  // Auth submissions still forward to Django below.`r`n",
        1
    )
    $content2 = [regex]::Replace(
        $content2,
        '(?s)(if\s*\(!demoExplicitlyEnabled\)\s*\{\s*)showBackendNotice\(\);\s*',
        '$1',
        1
    )
    if ($content2 -match "You are viewing the static preview" -or $content2 -match "showBackendNotice\(\)") {
        throw "Could not safely remove the banner injection; original file was preserved."
    }
    [System.IO.File]::WriteAllText($source, $content2, (New-Object System.Text.UTF8Encoding($false)))
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py tools\build_static.py
} else {
    & python tools\build_static.py
}
if ($LASTEXITCODE -ne 0) {
    throw "Static rebuild failed. See the Python error above."
}

$builtJs = Join-Path $root "site\js\demo-forms.js"
if (-not (Test-Path $builtJs)) { throw "Generated site JS was not found." }
if ([System.IO.File]::ReadAllText($builtJs).Contains("You are viewing the static preview")) {
    throw "Banner text remains in generated JS; inspect build output."
}
Write-Host "SUCCESS: static-preview banner removed from source and generated site."
Write-Host "Static preview can still forward sign-in/signup submissions to Django."
Write-Host "Real application: http://127.0.0.1:8000/"
Write-Host "Hard-refresh browser with Ctrl+Shift+R."
