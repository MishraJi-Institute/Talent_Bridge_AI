# TalentBridgeAI — Day 5 Database Backup and Inventory

**Date:** 2026-11-18  
**Roadmap day:** Day 5 only  
**Status:** COMPLETE  
**Constraint honored:** No migrate, no flush, no DROP/TRUNCATE, no record edits, no engine change, no restore-over-original. No passwords or PII in this report.

---

## A. Project and database identification

| Item | Verified value |
| --- | --- |
| Project root | `E:\Job POrtal\TalentBridgeAI` |
| Effective settings module | `config.settings` |
| Settings file | `backend\legacy-django\config\settings.py` |
| Database engine | **SQLite** (`django.db.backends.sqlite3`) |
| Database identity (file) | `E:\Job POrtal\TalentBridgeAI\database\TalentBridgeAI.sqlite3` |
| Configuration source | `DB_ENGINE` / `DB_NAME` via `.env` + settings (defaults: `sqlite` / `TalentBridgeAI`) |
| Connection options | `timeout: 20` |
| Database routers | **None** configured |
| Alternate engines in settings | MySQL branch exists but **not** active |
| Journal mode (source) | `delete` (WAL **not** enabled; no `-wal`/`-shm` files) |
| Pre-backup state | Managed Django server running (read/write app traffic possible); no migration/import/export task active |
| Disk free (drive E:) | ~173 GiB free before backup (sufficient) |

Connection verified by successful read-only SQLite open, ORM counts, and `showmigrations`.

---

## B. Backup details

| Item | Value |
| --- | --- |
| Backup directory | `E:\Job POrtal\TalentBridgeAI\backups\TalentBridgeAI_Day5_Database_Backup_2026-11-18_12-30-27\` |
| Backup filename | `TalentBridgeAI_Day5_Database_Backup_2026-11-18_12-30-27.sqlite3` |
| Full path | `E:\Job POrtal\TalentBridgeAI\backups\TalentBridgeAI_Day5_Database_Backup_2026-11-18_12-30-27\TalentBridgeAI_Day5_Database_Backup_2026-11-18_12-30-27.sqlite3` |
| Creation timestamp | 2026-11-18 12:30:27 (local) |
| Source size | **397,312** bytes |
| Backup size | **397,312** bytes |
| SHA-256 | `527adc391383e1ee9a46abd9a6d84b92e3b1094e4fe0a2b91ff5f6aad9892602` |
| Backup method | Python `sqlite3.Connection.backup()` online consistent copy into a **new** file (original not overwritten) |
| Companion inventory | `INVENTORY.txt`, `showmigrations.txt`, `showmigrations_plan.txt` in the same backup folder |

### Verification

| Check | Result |
| --- | --- |
| Backup file exists | **Yes** |
| Non-empty / size plausible | **Yes** (matches source byte size) |
| `PRAGMA integrity_check` on backup | **`ok`** |
| `PRAGMA quick_check` on backup | **`ok`** |
| Table name set vs source | **Match** (30 application tables; excludes internal `sqlite_*`) |
| Per-table `COUNT(*)` vs source | **Match** (`counts_match=True`) |
| Original DB still present | **Yes** (`database\TalentBridgeAI.sqlite3`, 397,312 bytes) |
| Restore-over-original | **Not performed** (forbidden on Day 5) |
| Restorability claim | **Not claimed** — integrity OK; full restore drill not authorized |

---

## C. Database inventory (read-only)

**Tables inspected:** 30 (user tables in `sqlite_master`, excluding `sqlite_%` internals).

| Table | App / area | Count | Status |
| --- | --- | ---: | --- |
| `auth_user` | auth | 2 | Populated |
| `auth_group` | auth | 0 | Empty |
| `auth_group_permissions` | auth | 0 | Empty |
| `auth_permission` | auth | 100 | Populated |
| `auth_user_groups` | auth | 0 | Empty |
| `auth_user_user_permissions` | auth | 0 | Empty |
| `django_admin_log` | admin | 6 | Populated |
| `django_content_type` | contenttypes | 25 | Populated |
| `django_migrations` | Django | 49 | Populated |
| `django_session` | sessions | 12 | Populated |
| `django_site` | sites | 1 | Populated |
| `account_emailaddress` | allauth.account | 0 | Empty |
| `account_emailconfirmation` | allauth.account | 0 | Empty |
| `socialaccount_socialaccount` | allauth.socialaccount | 0 | Empty |
| `socialaccount_socialapp` | allauth.socialaccount | 1 | Populated |
| `socialaccount_socialapp_sites` | allauth.socialaccount | 1 | Populated |
| `socialaccount_socialtoken` | allauth.socialaccount | 0 | Empty |
| `jobs_company` | jobs | 3 | Populated |
| `jobs_job` | jobs | 0 | Empty |
| `jobs_profile` | jobs | 1 | Populated |
| `jobs_signuprecord` | jobs | 1 | Populated |
| `jobs_resumedraft` | jobs | 0 | Empty |
| `jobs_application` | jobs | 0 | Empty |
| `jobs_applicationstatusevent` | jobs | 0 | Empty |
| `jobs_contactinquiry` | jobs | 0 | Empty |
| `jobs_savedjob` | jobs | 0 | Empty |
| `jobs_notification` | jobs | 0 | Empty |
| `jobs_jobalertpreference` | jobs | 0 | Empty |
| `jobs_jobalert` | jobs | 0 | Empty |
| `jobs_interview` | jobs | 0 | Empty |

**No row contents, emails, names, or resume files were exported.**

---

## D. Migration status

**Commands executed (read-only):**

- `python manage.py showmigrations`
- `python manage.py showmigrations --plan`

**Not executed:** `migrate`, `makemigrations`, `migrate --fake`, or any schema-altering SQL.

| App | Migrations on disk | Status |
| --- | --- | --- |
| `account` (allauth) | 0001–0009 | All **applied** `[X]` |
| `admin` | 0001–0003 | All applied |
| `auth` | 0001–0012 | All applied |
| `contenttypes` | 0001–0002 | All applied |
| `jobs` | 0001–0014 | All applied |
| `sessions` | 0001 | Applied |
| `sites` | 0001–0002 | All applied |
| `socialaccount` | 0001–0006 | All applied |

| Metric | Value |
| --- | ---: |
| Applied migration records (`[X]` lines) | **49** |
| Unapplied (`[ ]`) | **0** |
| `django_migrations` row count | **49** |
| Detected conflicts / multiple leaf nodes | **None observed** from `showmigrations` / `--plan` |

Artifacts: backup folder `showmigrations.txt`, `showmigrations_plan.txt`.

---

## E. Sample / operational record summary (counts only)

| Category | Model / table | Exists? | Approx. count |
| --- | --- | --- | ---: |
| Users / accounts | `auth.User` / `auth_user` | Yes | 2 |
| Candidate/employer profiles | `jobs.Profile` | Yes | 1 |
| Signup audit | `jobs.SignupRecord` | Yes | 1 |
| Companies | `jobs.Company` | Yes | 3 |
| Jobs | `jobs.Job` | Yes | 0 |
| Applications | `jobs.Application` | Yes | 0 |
| Application status history | `jobs.ApplicationStatusEvent` | Yes | 0 |
| Resume drafts | `jobs.ResumeDraft` | Yes | 0 |
| Saved jobs | `jobs.SavedJob` | Yes | 0 |
| Notifications | `jobs.Notification` | Yes | 0 |
| Job alerts | `jobs.JobAlert` + preference | Yes | 0 / 0 |
| Interviews | `jobs.Interview` | Yes | 0 |
| Contact inquiries | `jobs.ContactInquiry` | Yes | 0 |
| Education / Experience / Skill entities | — | **Not found** as models | — |
| CompanyMember | — | **Not found** | — |
| Dedicated AuditLog | — | **Not found** (partial: `django_admin_log` = 6) | — |

---

## F. Safety verification

| Check | Result |
| --- | --- |
| Database reset / delete | **Did not occur** |
| Records intentionally modified | **No** |
| Migrations applied | **No** |
| Original DB preserved | **Yes** |
| Backup separate new file | **Yes** (timestamped directory; no overwrite) |
| Git exclusion | `.gitignore` includes `backups/` and `*.sqlite3` |
| Git tracking | No `.git` in this workspace copy; exclusion still recorded for future repos |
| Public URL exposure | No Django routes serve `backups/` or `database/` (confirmed no matches in `config/urls.py`) |
| Not under `frontend/`, `static/`, or public media | Backup under `backups/` |
| Secrets / PII in this report | **None** |

---

## G. Outstanding issues / future observations

| Item | Notes | Approval needed? |
| --- | --- | --- |
| Empty `jobs_job` table | Jobs UI may use demo fallback (Day 2 observation) | Product/data decision later |
| Missing Education/Skill/CompanyMember models | Architecture gap for later ERD day | Yes before schema work |
| No restore drill | Day 5 forbids restore-over-live; optional restore-to-scratch later | Yes |
| Live server during backup | SQLite `backup()` API used for consistency | N/A |

**Day 6+ not started.**

---

## Commands / checks actually executed

1. Terminal idle check (managed runserver present; no migrate/backup conflict).  
2. Disk free space check on `E:`.  
3. Django `setup()` → confirm engine + `DATABASES['default']['NAME']`.  
4. Read-only PRAGMA / table list / counts on source.  
5. `sqlite3.Connection.backup()` → new timestamped file.  
6. `PRAGMA integrity_check` + `quick_check` on backup.  
7. Table/count comparison source vs backup.  
8. SHA-256 of backup file.  
9. `showmigrations` and `showmigrations --plan`.  
10. ORM `.count()` for jobs models + User (no field dumps).  
11. Confirm original file still exists; `.gitignore` patterns; no public backup routes.

---

## Final Day 5 status: COMPLETE

Backup created, integrity-verified, inventory and migration status recorded. Original database untouched aside from normal concurrent application use during the online backup API call.
