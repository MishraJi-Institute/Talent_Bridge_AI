param(
    [switch]$IfMissing,
    [switch]$NoServer
)

$ErrorActionPreference = "Stop"
$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
$DjangoDir = Join-Path $ProjectRoot "backend\legacy-django"
$EnvFile = Join-Path $ProjectRoot ".env"
$ExampleEnvFile = Join-Path $ProjectRoot ".env.example"
$Python = Join-Path $DjangoDir ".venv\Scripts\python.exe"
$Manager = Join-Path $ProjectRoot "tools\windows_manager.py"
$Manage = Join-Path $DjangoDir "manage.py"

function Test-EnvValue {
    param([string]$Name)

    if (-not (Test-Path -LiteralPath $EnvFile)) {
        return $false
    }

    $pattern = "^\s*$([regex]::Escape($Name))\s*=\s*(.*?)\s*$"
    foreach ($line in [System.IO.File]::ReadAllLines($EnvFile)) {
        if ($line -match $pattern) {
            $value = $Matches[1].Trim().Trim('"').Trim("'")
            return -not [string]::IsNullOrWhiteSpace($value)
        }
    }
    return $false
}

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Host "Google OAuth setup failed: the project virtual environment is missing." -ForegroundColor Red
    Write-Host "Run START_TALENTBRIDGEAI.bat once, then run this setup again."
    exit 1
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    if (-not (Test-Path -LiteralPath $ExampleEnvFile)) {
        Write-Host "Google OAuth setup failed: neither the project .env nor .env.example exists." -ForegroundColor Red
        exit 1
    }
    Copy-Item -LiteralPath $ExampleEnvFile -Destination $EnvFile
}

$hasClientId = Test-EnvValue "GOOGLE_OAUTH_CLIENT_ID"
$hasClientSecret = Test-EnvValue "GOOGLE_OAUTH_CLIENT_SECRET"
$useExistingCredentials = $IfMissing -and $hasClientId -and $hasClientSecret

Write-Host ""
Write-Host "TalentBridgeAI - Google OAuth local setup" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host "Credentials are stored only in the ignored project-root .env file."
Write-Host "Do not share the .env file or paste credentials into chat."

if (-not $useExistingCredentials) {
    $ClientId = Read-Host "Google OAuth Web Client ID"
    if ([string]::IsNullOrWhiteSpace($ClientId) -or
        $ClientId -notmatch "^[^@\s]+\.apps\.googleusercontent\.com$") {
        Write-Host "Google OAuth setup failed: enter a non-empty Web Client ID ending in .apps.googleusercontent.com." -ForegroundColor Red
        exit 1
    }

    $SecureSecret = Read-Host "Google OAuth Client Secret (input hidden)" -AsSecureString
    $Ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureSecret)
    try {
        $ClientSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($Ptr).Trim()
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr)
    }

    if ([string]::IsNullOrWhiteSpace($ClientSecret)) {
        $ClientSecret = $null
        $SecureSecret = $null
        Write-Host "Google OAuth setup failed: Client Secret cannot be empty." -ForegroundColor Red
        exit 1
    }

    $lines = @()
    if (Test-Path -LiteralPath $EnvFile) {
        $lines = [System.IO.File]::ReadAllLines($EnvFile)
    }
    $preservedLines = @($lines | Where-Object {
        $_ -notmatch '^\s*GOOGLE_OAUTH_CLIENT_ID\s*=' -and
        $_ -notmatch '^\s*GOOGLE_OAUTH_CLIENT_SECRET\s*='
    })
    $preservedLines += "GOOGLE_OAUTH_CLIENT_ID=$ClientId"
    $preservedLines += "GOOGLE_OAUTH_CLIENT_SECRET=$ClientSecret"
    [System.IO.File]::WriteAllLines(
        $EnvFile,
        [string[]]$preservedLines,
        [System.Text.UTF8Encoding]::new($false)
    )

    $ClientSecret = $null
    $SecureSecret = $null
    $Ptr = $null
}
else {
    Write-Host "Both credential entries are present; checking Django's loaded configuration without displaying values."
}

$env:DJANGO_ENV = "development"
$env:DJANGO_DEBUG = "true"
Push-Location $DjangoDir
try {
    & $Python $Manage check_google_oauth
    if ($LASTEXITCODE -ne 0) {
        throw "Django could not load both Google OAuth values from its configuration."
    }

    & $Python $Manage sync_google_oauth
    if ($LASTEXITCODE -ne 0) {
        throw "Google OAuth provider synchronization failed."
    }

    & $Python $Manage check
    if ($LASTEXITCODE -ne 0) {
        throw "Django system checks failed."
    }
}
catch {
    Write-Host "Google OAuth setup failed. Credentials were not displayed. Review the health-check output above." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host "Google OAuth configuration was verified by Django; credential values were not displayed." -ForegroundColor Green
if ($NoServer) {
    Write-Host "Restart Django to load the new settings:"
    Write-Host "  STOP_TALENTBRIDGEAI.bat"
    Write-Host "  START_TALENTBRIDGEAI.bat"
    exit 0
}

Write-Host "Restarting the managed Django server. Startup is reported successful only after its HTTP health check returns 200."
& $Python $Manager stop
if ($LASTEXITCODE -ne 0) {
    Write-Host "Google OAuth was configured, but the managed server could not be stopped safely. Use STOP_TALENTBRIDGEAI.bat, then START_TALENTBRIDGEAI.bat." -ForegroundColor Red
    exit 1
}

& $Python $Manager start
if ($LASTEXITCODE -ne 0) {
    Write-Host "Google OAuth was configured, but Django did not start successfully. Review logs\setup.log and logs\server.log." -ForegroundColor Red
    exit 1
}
