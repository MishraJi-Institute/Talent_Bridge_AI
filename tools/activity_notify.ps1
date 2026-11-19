# TalentBridgeAI activity notification.
# Built-in Windows APIs only. Does not change system settings or install software.
param(
    [Parameter(Mandatory = $true)][string]$Current,
    [ValidateSet("working", "thinking", "waiting", "blocked", "completed", "error")]
    [string]$Kind = "working",
    [string]$Phase = "",
    [string]$Target = "",
    [string]$Last = "",
    [string]$Next = "",
    [string]$ErrorText = "",
    [ValidateSet(
        "notification-test",
        "development-started",
        "feature-completed",
        "tests-finished",
        "bug-fixed-verified",
        "oauth-succeeded",
        "oauth-failed",
        "checkpoint-saved",
        "paused-safely",
        "development-resumed",
        "project-completed",
        "final-files-ready"
    )]
    [string]$Milestone = "",
    [switch]$Audible,
    [switch]$NoVoice
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$logDir = Join-Path $root "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logPath = Join-Path $logDir "activity.log"

function Write-ActivityLog {
    param([string]$Message)
    Add-Content -Path $logPath -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | $Message" -Encoding utf8
}

function Get-MilestoneAnnouncement {
    param([string]$Event)
    switch ($Event) {
        "notification-test" { return "Testing the TalentBridge AI notifications." }
        "development-started" { return "TalentBridge AI development started." }
        "feature-completed" { return "A development milestone has been completed." }
        "tests-finished" { return "Testing completed. Please review the results." }
        "bug-fixed-verified" { return "A bug fix has been verified." }
        "oauth-succeeded" { return "Google OAuth verification succeeded." }
        "oauth-failed" { return "Google OAuth verification failed." }
        "checkpoint-saved" { return "Checkpoint saved successfully." }
        "paused-safely" { return "TalentBridge AI development is paused." }
        "development-resumed" { return "TalentBridge AI development has resumed." }
        "project-completed" { return "TalentBridge AI project is ready for final review." }
        "final-files-ready" { return "The final PDF and ZIP are ready." }
    }
}

function Write-ActivityState {
    param(
        [string]$Status,
        [string]$StatusKind,
        [string]$StatusPhase,
        [string]$StatusTarget,
        [string]$StatusLast,
        [string]$StatusCurrent,
        [string]$StatusNext,
        [string]$StatusError,
        [string]$Updated
    )
    Set-Content -Path (Join-Path $logDir "agent_status.txt") -Value @(
        "state=$Status",
        "kind=$StatusKind",
        "phase=$StatusPhase",
        "target=$StatusTarget",
        "last=$StatusLast",
        "current=$StatusCurrent",
        "next=$StatusNext",
        "error=$StatusError",
        "updated=$Updated"
    ) -Encoding utf8

    $boardContent = @"
# TalentBridgeAI activity

Updated: $Updated

Status: $Status
Phase: $StatusPhase
Page, file, or feature: $StatusTarget
Last completed action: $StatusLast
Current action: $StatusCurrent
Next action: $StatusNext
Error or blocker: $(if ($StatusError) { $StatusError } else { "None" })

Chat cannot add a message while a tool call is still running. This file is the live status. logs/activity.log keeps the history. When tools/activity_pulse.ps1 is running, it sends a Windows balloon about every 2 minutes while the activity heartbeat is fresh. Sounds and short spoken announcements are sent only for marked milestones, not routine file edits.
"@
    Set-Content -Path (Join-Path $root "ACTIVITY_NOW.md") -Value $boardContent -Encoding utf8
}

$now = Get-Date
$stamp = $now.ToString("yyyy-MM-dd HH:mm:ss")
$state = switch ($Kind) {
    "thinking" { "THINKING" }
    "waiting" { "WAITING" }
    "blocked" { "BLOCKED" }
    "completed" { "COMPLETED" }
    "error" { "BLOCKED" }
    default { "WORKING" }
}
if ($Milestone -eq "oauth-failed") { $state = "BLOCKED" }
if ($Milestone -in @("oauth-succeeded", "project-completed", "final-files-ready")) { $state = "COMPLETED" }
if ($Milestone -eq "paused-safely") { $state = "PAUSED" }
if ($Kind -eq "error" -and -not $ErrorText) { $ErrorText = $Current }

$line = "$stamp | $state | $Phase | $Target | last: $Last | now: $Current | next: $Next"
if ($Milestone) { $line += " | event: $Milestone" }
if ($ErrorText) { $line += " | error: $ErrorText" }
Add-Content -Path $logPath -Value $line -Encoding utf8
Set-Content -Path (Join-Path $logDir "agent_heartbeat.txt") -Value $stamp -Encoding utf8
Write-ActivityState -Status $state -StatusKind $Kind -StatusPhase $Phase -StatusTarget $Target -StatusLast $Last -StatusCurrent $Current -StatusNext $Next -StatusError $ErrorText -Updated $stamp

$shouldNotifyAudibly = $Audible -or $Milestone -or $Kind -in @("blocked", "error", "completed")
$audioLock = $null
$audioLockAcquired = $false
$audioStatus = "AUDIO_SKIPPED"
$voiceStatus = "VOICE_SKIPPED"
$audioDiagnostic = "AUDIO_DIAGNOSTICS_UNAVAILABLE"
$wav = $null

if ($shouldNotifyAudibly) {
    try {
        $serviceStates = @()
        foreach ($serviceName in @("Audiosrv", "AudioEndpointBuilder")) {
            $service = Get-Service -Name $serviceName -ErrorAction Stop
            $serviceStates += "$serviceName=$($service.Status)"
        }

        $endpoints = @()
        if (Get-Command Get-PnpDevice -ErrorAction SilentlyContinue) {
            $endpoints = @(Get-PnpDevice -Class AudioEndpoint -Status OK -ErrorAction Stop |
                Where-Object { $_.FriendlyName -notmatch "Microphone|Input" } |
                Select-Object -ExpandProperty FriendlyName)
        }

        if (-not ("TbWaveProbe" -as [type])) {
            Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class TbWaveProbe {
    [DllImport("winmm.dll", SetLastError = true)]
    public static extern uint waveOutGetVolume(IntPtr device, out uint volume);
}
"@
        }
        [uint32]$unusedVolume = 0
        $defaultOutputResult = [TbWaveProbe]::waveOutGetVolume([IntPtr](-1), [ref]$unusedVolume)
        $defaultOutput = if ($defaultOutputResult -eq 0) { "DEFAULT_WAVE_OUTPUT_AVAILABLE" } else { "DEFAULT_WAVE_OUTPUT_UNAVAILABLE:$defaultOutputResult" }
        $endpointSummary = if ($endpoints.Count -gt 0) { ($endpoints -join ", ") } else { "no active render endpoint listed" }
        $audioDiagnostic = "$($serviceStates -join '; '); $defaultOutput; endpoints=$endpointSummary"
        Write-ActivityLog "AUDIO_DIAGNOSTIC | $audioDiagnostic"
    } catch {
        $audioDiagnostic = "AUDIO_DIAGNOSTIC_FAILED | $($_.Exception.Message)"
        Write-ActivityLog $audioDiagnostic
    }

    $lockPath = Join-Path $logDir "notification_audio.lock"
    for ($attempt = 0; $attempt -lt 20 -and -not $audioLockAcquired; $attempt++) {
        try {
            $audioLock = [System.IO.File]::Open($lockPath, "OpenOrCreate", "ReadWrite", "None")
            $audioLockAcquired = $true
        } catch [System.IO.IOException] {
            Start-Sleep -Milliseconds 250
        }
    }

    if (-not $audioLockAcquired) {
        $audioStatus = "AUDIO_LOCK_TIMEOUT"
        Write-ActivityLog "AUDIO_FAILURE | $audioStatus"
    } else {
        try {
            $preferredWav = "C:\Windows\Media\Windows Notify.wav"
            if ($Kind -in @("blocked", "error") -or $Milestone -in @("oauth-failed")) {
                $preferredWav = "C:\Windows\Media\Windows Exclamation.wav"
            }
            $wavCandidates = @(
                $preferredWav,
                "C:\Windows\Media\Windows Notify.wav",
                "C:\Windows\Media\Windows Exclamation.wav",
                "C:\Windows\Media\Windows Default.wav",
                "C:\Windows\Media\tada.wav"
            ) | Select-Object -Unique

            foreach ($candidate in $wavCandidates) {
                if (-not (Test-Path -LiteralPath $candidate)) { continue }
                try {
                    $player = New-Object System.Media.SoundPlayer($candidate)
                    $player.Load()
                    $player.PlaySync()
                    $wav = $candidate
                    $audioStatus = "AUDIO_PLAYBACK_SUCCEEDED; method=SoundPlayer.PlaySync; file=$wav"
                    break
                } catch {
                    Write-ActivityLog "AUDIO_FILE_FAILED | file=$candidate | error=$($_.Exception.Message)"
                } finally {
                    if ($player) { $player.Dispose(); $player = $null }
                }
            }

            if (-not $wav) {
                try {
                    if ($Kind -in @("blocked", "error") -or $Milestone -eq "oauth-failed") {
                        [System.Media.SystemSounds]::Exclamation.Play()
                    } else {
                        [System.Media.SystemSounds]::Asterisk.Play()
                    }
                    Start-Sleep -Milliseconds 1200
                    $audioStatus = "SYSTEM_SOUND_API_CALL_SUCCEEDED; playback completion cannot be confirmed"
                } catch {
                    $audioStatus = "AUDIO_PLAYBACK_FAILED | $($_.Exception.Message)"
                }
            }
            Write-ActivityLog $audioStatus

            if ($Milestone -and -not $NoVoice) {
                $speaker = $null
                try {
                    $speaker = New-Object -ComObject SAPI.SpVoice
                    if ($speaker.GetVoices().Count -gt 0) {
                        [void]$speaker.Speak((Get-MilestoneAnnouncement $Milestone), 0)
                        $voiceStatus = "VOICE_SPEAK_SUCCEEDED; method=SAPI.SpVoice"
                    } else {
                        $voiceStatus = "VOICE_UNAVAILABLE; no installed SAPI voices"
                    }
                } catch {
                    $voiceStatus = "VOICE_FAILED | $($_.Exception.Message)"
                } finally {
                    if ($speaker) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($speaker) }
                }
                Write-ActivityLog $voiceStatus
            }
        } finally {
            $audioLock.Dispose()
        }
    }
}

$audioFailed = $audioStatus -match "AUDIO_PLAYBACK_FAILED|AUDIO_LOCK_TIMEOUT"
if ($audioFailed) {
    $ErrorText = "Audio notification failed; requesting visible fallback. $audioStatus"
    $Current = "Audio notification failed; using visible fallback."
    Write-ActivityLog "NOTIFICATION_DEGRADED | Audio failed; visible notification requested."
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-ActivityState -Status $state -StatusKind $Kind -StatusPhase $Phase -StatusTarget $Target -StatusLast $Last -StatusCurrent $Current -StatusNext $Next -StatusError $ErrorText -Updated $stamp
}

$visualStatus = "BALLOON_NOT_ATTEMPTED"
$icon = $null
try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $icon = New-Object System.Windows.Forms.NotifyIcon
    $icon.Icon = [System.Drawing.SystemIcons]::Information
    $icon.Visible = $true
    $icon.BalloonTipTitle = "TalentBridgeAI - $state"
    $tip = $Current
    if ($Next) { $tip += " Next: $Next" }
    if ($tip.Length -gt 220) { $tip = $tip.Substring(0, 220) }
    $icon.BalloonTipText = $tip
    $icon.ShowBalloonTip(4000)
    Start-Sleep -Milliseconds 4200
    $visualStatus = "BALLOON_REQUEST_SUCCEEDED; display not user-confirmed"
} catch {
    $visualStatus = "BALLOON_FAILED | $($_.Exception.Message)"
} finally {
    if ($icon) { $icon.Dispose() }
}
Write-ActivityLog "VISUAL_NOTIFICATION | $visualStatus"

$visualFailed = $visualStatus -match "BALLOON_FAILED"
if ($audioFailed -and $visualFailed) {
    $state = "BLOCKED"
    $Current = "All progress notification channels failed."
    $Next = "Pause development safely and save a checkpoint."
    $ErrorText = "Audio: $audioStatus; visual: $visualStatus"
    Write-ActivityLog "NOTIFICATION_FAILURE_CHECKPOINT | Development must pause; save a safe checkpoint before continuing."
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-ActivityState -Status $state -StatusKind $Kind -StatusPhase $Phase -StatusTarget $Target -StatusLast $Last -StatusCurrent $Current -StatusNext $Next -StatusError $ErrorText -Updated $stamp
}

Write-Output $audioDiagnostic
Write-Output $audioStatus
Write-Output $voiceStatus
Write-Output $visualStatus
Write-Output "NOTIFIED $state"
