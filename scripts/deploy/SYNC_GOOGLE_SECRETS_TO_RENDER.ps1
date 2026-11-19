<#
.SYNOPSIS
  Merge local Google OAuth secrets into the Render web service (keeps other env vars).

.REQUIREMENTS
  RENDER_API_KEY + local .env Google values + Blueprint service talentbridge-ai
#>
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$EnvFile = Join-Path $Root '.env'

$apiKey = $env:RENDER_API_KEY
if (-not $apiKey) {
  throw 'Set RENDER_API_KEY first (Render → Account Settings → API Keys).'
}
if (-not (Test-Path -LiteralPath $EnvFile)) {
  throw "Missing $EnvFile"
}

function Get-DotEnvValue([string]$name) {
  $line = Get-Content -LiteralPath $EnvFile | Where-Object { $_ -match "^$([regex]::Escape($name))=" } | Select-Object -First 1
  if (-not $line) { return '' }
  return ($line.Substring($name.Length + 1)).Trim()
}

$clientId = Get-DotEnvValue 'GOOGLE_OAUTH_CLIENT_ID'
$clientSecret = Get-DotEnvValue 'GOOGLE_OAUTH_CLIENT_SECRET'
if (-not $clientId -or -not $clientSecret) {
  throw 'GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET must be set in .env'
}

$headers = @{
  Authorization = "Bearer $apiKey"
  Accept        = 'application/json'
  'Content-Type' = 'application/json'
}

Write-Host 'Looking up Render services...'
$services = Invoke-RestMethod -Headers $headers -Uri 'https://api.render.com/v1/services?limit=50'
$svc = foreach ($row in @($services)) {
  $item = if ($row.service) { $row.service } else { $row }
  if ($item.name -eq 'talentbridge-ai') { $item; break }
}
if (-not $svc) {
  throw "Service 'talentbridge-ai' not found. Create it first via Render Blueprint (render.yaml)."
}

$serviceId = $svc.id
Write-Host "Merging Google secrets into service $serviceId..."

$existing = Invoke-RestMethod -Headers $headers -Uri "https://api.render.com/v1/services/$serviceId/env-vars"
$merged = @{}
foreach ($row in @($existing)) {
  $ev = if ($row.envVar) { $row.envVar } else { $row }
  if ($ev.key) { $merged[$ev.key] = $ev.value }
}
$merged['GOOGLE_OAUTH_CLIENT_ID'] = $clientId
$merged['GOOGLE_OAUTH_CLIENT_SECRET'] = $clientSecret
$merged['DJANGO_ENV'] = 'production'
$merged['DJANGO_DEBUG'] = 'false'
$merged['DJANGO_BEHIND_PROXY'] = 'true'
$merged['DJANGO_SECURE_SSL_REDIRECT'] = 'true'

$bodyObj = @()
foreach ($key in $merged.Keys) {
  $bodyObj += @{ key = $key; value = [string]$merged[$key] }
}
$body = ConvertTo-Json -InputObject $bodyObj -Depth 4

Invoke-RestMethod -Method Put -Headers $headers -Uri "https://api.render.com/v1/services/$serviceId/env-vars" -Body $body | Out-Null
Invoke-RestMethod -Method Post -Headers $headers -Uri "https://api.render.com/v1/services/$serviceId/deploys" -Body '{}' | Out-Null

$hostName = $null
if ($svc.serviceDetails -and $svc.serviceDetails.hostName) {
  $hostName = $svc.serviceDetails.hostName
}
Write-Host 'Secrets synced and deploy triggered (no secrets printed).'
if ($hostName) {
  Write-Host "Open after live: https://$hostName/login/"
  Write-Host "Google callback: https://$hostName/accounts/google/login/callback/"
}
