# Step 2 test report

Date: 2026-11-12

Commands used the project virtual environment at `legacy-django\.venv`. Secret values were not printed.

## Passed

| Check | Result |
| --- | --- |
| `python manage.py check` | Passed. No issues. |
| `python manage.py showmigrations` | Every listed migration is applied, including `jobs` 0001–0007. No unapplied migration. |
| `python manage.py test jobs.tests.AdminTipBotTests jobs.tests.SocialAuthenticationTests jobs.tests.DjangoDashboardAuthTests` | 46 tests, OK, 65.5 seconds. The test database was created and destroyed. The project SQLite file was not used for these tests. |
| Admin login page | `GET http://127.0.0.1:8000/admin/login/` returned HTTP 200. The stray CSS fragment was absent. The office background image reference was present. |
| Google configuration | After restart, `prepare_local_auth` reported OAuth loaded: yes, callback `/accounts/google/login/callback/`, site `127.0.0.1:8000`, and a database sync with `created=True` then `created=False` on the next start. The stored app is linked to site 1 and matches the loaded settings. `manage.py check_google_oauth` reported both values loaded. |
| Live login page | `GET /login/` returned HTTP 200. The Google button was not disabled. |
| Homepage | `GET /` returned HTTP 200 after the final start. |
| Stop | The managed process tree was stopped. Port 8000 then had no listener. |
| Start | A new process reached HTTP 200. A second start detected PID 17764 and left it running. |
| User data | `auth_user` count was 0 before the restart and 0 after the final start. |

## Failed

None of the checks above failed.

## Not tested

- Google account chooser, consent, callback login, and cancellation in a real browser. An enabled button is not a completed sign-in.
- Signing in to Django admin. No superuser exists, and this step did not create one.
- The full `jobs` suite from the earlier checkpoint (previously reported as 78 tests). This step ran the 46 authentication and admin tests listed above.

## Server state at the end of this step

Django was running at `http://127.0.0.1:8000/` under the managed start process. `START_TALENTBRIDGEAI.bat` will see it and will not reload `.env` again. Use `RESTART_TALENTBRIDGEAI.bat` after the next configuration change, and leave that window open.
