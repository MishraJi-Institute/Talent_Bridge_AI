# Sends a status balloon every 2 minutes.
# A fresh agent heartbeat keeps the saved status. A stale heartbeat is reported as not working.
# Audible notifications are reserved for explicit milestones in activity_notify.ps1.
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$logDir = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$lockPath = Join-Path $logDir "activity_pulse.lock"
$heartbeatPath = Join-Path $logDir "agent_heartbeat.txt"
$statusPath = Join-Path $logDir "agent_status.txt"
$logPath = Join-Path $logDir "activity.log"

$lock = [System.IO.File]::Open($lockPath, "OpenOrCreate", "ReadWrite", "None")
try {
    $lock.SetLength(0)
    $bytes = [Text.Encoding]::UTF8.GetBytes("$PID")
    $lock.Write($bytes, 0, $bytes.Length)
    $lock.Flush()

    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    while ($true) {
        $state = "NOT WORKING"
        $current = "No task is running."
        $phase = "Activity monitor"
        $next = ""
        $updated = "unknown"
        $fresh = $false

        if (Test-Path $heartbeatPath) {
            $beat = (Get-Content $heartbeatPath -Raw).Trim()
            $beatTime = [datetime]::MinValue
            if ([datetime]::TryParse($beat, [ref]$beatTime)) {
                $updated = $beatTime.ToString("yyyy-MM-dd HH:mm:ss")
                if (((Get-Date) - $beatTime).TotalMinutes -le 4) { $fresh = $true }
            }
        }

        if ($fresh -and (Test-Path $statusPath)) {
            $map = @{}
            Get-Content $statusPath | ForEach-Object {
                $pair = $_.Split("=", 2)
                if ($pair.Length -eq 2) { $map[$pair[0]] = $pair[1] }
            }
            if ($map["state"]) { $state = $map["state"] }
            if ($map["current"]) { $current = $map["current"] }
            elseif ($map["message"]) { $current = $map["message"] }
            if ($map["phase"]) { $phase = $map["phase"] }
            if ($map["next"]) { $next = $map["next"] }
        } elseif (-not $fresh) {
            $current = "No task is running. Last agent update: $updated."
            $next = "Wait for a new chat reply or a WORKING status."
        }

        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $logPath -Value "$stamp | PULSE | $state | $phase | $current | next: $next" -Encoding utf8

        $icon = New-Object System.Windows.Forms.NotifyIcon
        $icon.Icon = [System.Drawing.SystemIcons]::Information
        $icon.Visible = $true
        $icon.BalloonTipTitle = "TalentBridgeAI - $state"
        $tip = "$state. $current"
        if ($next) { $tip += " Next: $next" }
        if ($tip.Length -gt 220) { $tip = $tip.Substring(0, 220) }
        $icon.BalloonTipText = $tip
        $icon.ShowBalloonTip(4000)
        Start-Sleep -Milliseconds 900
        $icon.Dispose()

        Start-Sleep -Seconds 120
    }
} finally {
    $lock.Dispose()
    Remove-Item $lockPath -Force -ErrorAction SilentlyContinue
}
