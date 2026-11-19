# Development notifications

The existing notification system is maintained in `tools/activity_notify.ps1` and `tools/activity_pulse.ps1`. It records status in `ACTIVITY_NOW.md`, appends history to `logs/activity.log`, updates the heartbeat/status files, and uses a Windows tray balloon. The pulse script continues its visual status updates when explicitly run; it no longer repeats sounds on a timer. This task did not leave the pulse loop running. Audible notices are reserved for explicitly marked milestones.

## Milestones

Call the existing notifier once when a milestone actually occurs. Do not mark an event complete before its work or verification succeeds.

| Event | Milestone value |
| --- | --- |
| Manual notification test | `notification-test` |
| Major development task starts | `development-started` |
| Major feature is completed | `feature-completed` |
| Test suite finishes | `tests-finished` |
| Bug fix is verified | `bug-fixed-verified` |
| Google OAuth verification succeeds / fails | `oauth-succeeded` / `oauth-failed` |
| Development checkpoint is saved | `checkpoint-saved` |
| Development is safely paused / resumes | `paused-safely` / `development-resumed` |
| Whole project is complete | `project-completed` |
| Final PDF and ZIP are ready and verified | `final-files-ready` |

Example from the project directory. This uses a child PowerShell process with a process-only execution-policy override; it does not change the stored Windows policy:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\activity_notify.ps1 `
  -Current "The focused test run has finished; reviewing its results." `
  -Kind working `
  -Phase "Verification" `
  -Target "Development test suite" `
  -Last "Implementation is complete." `
  -Next "Review the test results." `
  -Milestone tests-finished
```

For OAuth events, use only a generic `Current`, `Target`, and `ErrorText`; never put client IDs, secrets, tokens, account details, or other sensitive values in a spoken announcement. Spoken messages are fixed, short, generic phrases and do not read status text aloud. Speech uses Windows SAPI (`SAPI.SpVoice`) when an installed voice is available; `-NoVoice` disables speech for a particular notification.

## Playback behavior and verification

- Preferred sound: `C:\Windows\Media\Windows Notify.wav`; failure notices prefer `Windows Exclamation.wav`. The notifier checks the Windows Default and `tada.wav` files as alternatives.
- WAV playback uses `System.Media.SoundPlayer.PlaySync()` so one sound completes before another begins. A per-project exclusive audio lock serializes concurrent notification requests with a five-second acquisition limit.
- Before playback, the notifier records Windows Audio service states, queries the configured default wave output without changing volume, and lists active render endpoints when Windows exposes them.
- It tries installed WAV alternatives, then the Windows system-sound API. Audio and SAPI outcomes, the chosen file/method, and the visible balloon request are logged in `logs/activity.log`. The script does not change volume, select devices, start services, or change Windows settings.
- The tray icon is kept alive for the balloon request. A successful API call is recorded as a request, not proof that Windows displayed it or that a person saw it.
- If sound playback fails, the script records the error and updates the activity status while still attempting a visible notification. If both sound and the balloon fail for a milestone, it records a notification-failure checkpoint and marks progress blocked with an instruction to pause safely.
- The scripts do not start a background service or an infinite audio loop. The existing pulse process is only a visual status monitor.

To safely test the current setup, run the notifier explicitly:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\activity_notify.ps1 `
  -Current "Testing the Windows development notification." `
  -Kind working `
  -Phase "Notification verification" `
  -Target "Sound and speech test" `
  -Next "Confirm whether the sound was audible." `
  -Milestone notification-test
```

Inspect the command output and the latest `AUDIO_DIAGNOSTIC`, `AUDIO_PLAYBACK_SUCCEEDED`, `VOICE_SPEAK_SUCCEEDED`, and `VISUAL_NOTIFICATION` entries in `logs/activity.log`. A successful playback call does not prove that speakers/headphones produced sound or that it was heard. If uncertain, run the test while listening at the device and confirm the result; do not raise system volume as part of this test.

## Current machine check

The latest development check found:

- `C:\Windows\Media\Windows Notify.wav` and the Windows Exclamation, Default, and `tada.wav` alternatives exist and load as WAV files.
- `Audiosrv` and `AudioEndpointBuilder` were running.
- Windows listed the Realtek speakers/headphones output endpoint as OK, and the default wave-output probe succeeded. These checks do not prove the endpoint was audible.
- Windows SAPI was available with two installed voices.
- The development notification test at 23:14 and the final safe-pause notification at 23:17 both returned `AUDIO_PLAYBACK_SUCCEEDED` using `SoundPlayer.PlaySync()` with `Windows Notify.wav`, `VOICE_SPEAK_SUCCEEDED` using `SAPI.SpVoice`, and `BALLOON_REQUEST_SUCCEEDED`. The details and audio diagnostics are recorded in `logs/activity.log`.
- Historical activity entries also recorded successful synchronous playback calls and balloon requests. Neither those records nor the new test establish that the sound was heard.

Actual speaker/headphone output remains unconfirmed. The user must listen during a test to confirm audibility. Do not claim a sound was heard based only on script output.
