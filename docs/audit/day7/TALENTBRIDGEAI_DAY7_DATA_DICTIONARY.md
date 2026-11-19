# TalentBridgeAI — Day 7 Data Dictionary (Existing Implementation)

**Date:** 2026-11-18  
**Roadmap day:** Day 7 only  
**Source of truth:** `backend/legacy-django/jobs/models.py` + Django `_meta` introspection  
**Artifact:** `docs/reports/_day7_model_inventory.json`  
**Constraint:** Documentation only — no schema or data changes.

Concrete `jobs` models: **13** · Concrete fields documented: **103** · Relationships: **18** FK/O2O.

---

## Identity hub (framework — not a `jobs` model)

### `auth.User` (`auth_user`)

Django built-in user. All portal identity hangs off this table. Custom user model: **not used**.

Key columns used by TalentBridgeAI (framework fields; not re-declared in `jobs`): `id`, `username`, `email`, `password` (hashed), `is_active`, `is_staff`, `is_superuser`, `first_name`, `last_name`, `date_joined`, `last_login`.

Related reverse accessors from `jobs`: `profile`, `owned_company`, `signup_record`, `resume_draft`, `job_applications`, `saved_jobs`, `portal_notifications`, `job_alert_preferences`, `job_alerts`, `created_interviews`, `application_status_events`.

---

## 1. Company

| | |
| --- | --- |
| **Model** | `Company` |
| **App / table** | `jobs` / `jobs_company` |
| **Source** | `jobs/models.py` |
| **Purpose** | Employer company record; optional link to registering user; approval gate for publishing jobs |
| **Type** | Concrete |
| **Related** | User (owner), Job |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK / not null | PK | auto | — | Surrogate primary key |
| owner | OneToOneField | owner_id | blank; **null OK** | Unique (O2O) | — | → User, SET_NULL, `owned_company` | Registering employer account; nullable for legacy |
| is_approved | BooleanField | is_approved | required | — | `False` | — | Only approved employers may publish jobs |
| name | CharField(200) | name | required | — | — | — | Company display name |
| description | TextField | description | blank OK | — | `''` | — | Company description |
| logo | ImageField | logo | blank/null OK | — | — | file `company_logos/` | Logo under `MEDIA_ROOT` |
| website | URLField | website | blank OK | — | `''` | — | Company website |
| location | CharField(100) | location | blank OK | — | `''` | — | Free-text location |
| industry | CharField(100) | industry | blank OK | — | `''` | — | Industry label |
| created_at | DateTimeField | created_at | auto | — | auto_now_add | — | Creation timestamp |

### Constraints / indexes / Meta

- PK: `id`  
- O2O unique on `owner_id`  
- No custom Meta indexes/ordering  

### Lifecycle

- Created at employer signup / admin.  
- Delete User with SET_NULL leaves company; delete Company CASCADE deletes Jobs.

---

## 2. Job

| | |
| --- | --- |
| **Model** | `Job` |
| **Table** | `jobs_job` |
| **Purpose** | Job listing owned by a Company |
| **Related** | Company, Application, SavedJob, JobAlert |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| company | ForeignKey | company_id | required | FK index | — | → Company CASCADE `jobs` | Posting company |
| title | CharField(200) | title | required | — | — | — | Job title |
| description | TextField | description | required | — | — | — | Full description |
| requirements | TextField | requirements | blank OK | — | `''` | — | Requirements text |
| salary | CharField(100) | salary | blank OK | — | `''` | — | Salary display string (not numeric) |
| location | CharField(100) | location | blank OK | — | `''` | — | Free-text location |
| job_type | CharField(20) | job_type | required | — | `Full-time` / JOB_TYPE_CHOICES | — | Employment type |
| work_mode | CharField(20) | work_mode | required | — | `Hybrid` / On-site\|Hybrid\|Remote | — | Work mode |
| experience | CharField(100) | experience | blank OK | — | `''` | — | Experience requirement text |
| skills | CharField(200) | skills | blank OK | — | `''` | — | Comma-style skills string (not Skill entity) |
| is_active | BooleanField | is_active | required | — | `True` | — | Visibility/active flag |
| is_demo | BooleanField | is_demo | required | — | `False` | — | Sample listing; applications disabled in product logic |
| posted_at | DateTimeField | posted_at | auto | — | auto_now_add | — | Publish time |

**JOB_TYPE_CHOICES:** Full-time, Part-time, Contract, Internship, Freelance.

### Constraints / Meta

- FK to Company  
- No UniqueConstraint on title  
- No Meta indexes  

---

## 3. Profile

| | |
| --- | --- |
| **Model** | `Profile` |
| **Table** | `jobs_profile` |
| **Purpose** | Portal profile for seeker or employer (role on same model) |
| **Related** | User |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| role | CharField(20) | role | required | — | `job_seeker` / job_seeker\|employer | — | Account role |
| phone | CharField(30) | phone | blank OK | — | `''` | — | Phone |
| user | OneToOneField | user_id | required | Unique | — | → User CASCADE | Account link (imported `User` class) |
| full_name | CharField(100) | full_name | required | — | — | — | Display name |
| headline | CharField(200) | headline | blank OK | — | `''` | — | Headline |
| skills | CharField(200) | skills | blank OK | — | `''` | — | Skills string |
| experience | CharField(100) | experience | blank OK | — | `''` | — | Experience summary string |
| resume | FileField | resume | blank/null OK | — | — | file `resumes/` | Uploaded resume file |
| location | CharField(100) | location | blank OK | — | `''` | — | Location |
| bio | TextField | bio | blank OK | — | `''` | — | Biography |
| is_discoverable | BooleanField | is_discoverable | required | — | `False` | — | Candidate search visibility |

### Constraints / Meta

- O2O unique `user_id`  
- No timestamps on Profile  

---

## 4. SignupRecord

| | |
| --- | --- |
| **Model** | `SignupRecord` |
| **Table** | `jobs_signuprecord` |
| **Purpose** | One-time signup audit; unique email across registrations |
| **Meta** | `ordering = ('-created_at',)` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| user | OneToOneField | user_id | required | Unique | — | → User CASCADE `signup_record` | Account |
| email | EmailField(254) | email | required | **Unique** | — | — | Signup email (normalized in app flows) |
| signup_method | CharField(20) | signup_method | required | — | email_password \| google | — | How account was created |
| role | CharField(20) | role | blank OK | — | `''` | — | Role at signup (string; may mirror Profile.role) |
| email_verified | BooleanField | email_verified | required | — | `False` | — | Verification flag (product may still use ACCOUNT_EMAIL_VERIFICATION=none) |
| created_at | DateTimeField | created_at | auto | — | auto_now_add | — | Signup time |

---

## 5. ResumeDraft

| | |
| --- | --- |
| **Model** | `ResumeDraft` |
| **Table** | `jobs_resumedraft` |
| **Purpose** | Private editable resume draft JSON per user |
| **Admin** | **Not registered** |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| user | OneToOneField | user_id | required | Unique | — | → User CASCADE `resume_draft` | Owner |
| content | JSONField | content | blank OK | — | `dict` callable | — | Draft structure (education/experience may live here as JSON) |
| updated_at | DateTimeField | updated_at | auto | — | auto_now | — | Last edit |

---

## 6. Application

| | |
| --- | --- |
| **Model** | `Application` |
| **Table** | `jobs_application` |
| **Purpose** | Job application by a user |
| **Meta** | ordering `-submitted_at`; UniqueConstraint `(job, applicant)` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| job | ForeignKey | job_id | required | FK | — | → Job CASCADE `applications` | Target job |
| applicant | ForeignKey | applicant_id | required | FK | — | → User CASCADE `job_applications` | Applicant |
| cover_note | TextField | cover_note | blank OK | — | `''` | — | Cover note |
| status | CharField(20) | status | required | — | `applied` + STATUS_CHOICES | — | Workflow status (includes legacy values) |
| submitted_at | DateTimeField | submitted_at | auto | — | auto_now_add | — | Submission time |

**STATUS_CHOICES:** applied, under_review, shortlisted, interview_scheduled, selected, rejected, **pending**, **reviewed**.

---

## 7. ApplicationStatusEvent

| | |
| --- | --- |
| **Model** | `ApplicationStatusEvent` |
| **Table** | `jobs_applicationstatusevent` |
| **Purpose** | Append-only status change history |
| **Admin** | **Not registered** |
| **Meta** | ordering `-created_at` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| application | ForeignKey | application_id | required | FK | — | → Application CASCADE `status_events` | Parent application |
| from_status | CharField(20) | from_status | blank OK | — | `''` | — | Previous status |
| to_status | CharField(20) | to_status | required | — | — | — | New status |
| note | CharField(255) | note | blank OK | — | `''` | — | Optional note |
| changed_by | ForeignKey | changed_by_id | null/blank OK | FK | — | → User SET_NULL | Actor |
| created_at | DateTimeField | created_at | auto | — | auto_now_add | — | Event time |

**Soft delete:** None (hard CASCADE with application).

---

## 8. ContactInquiry

| | |
| --- | --- |
| **Model** | `ContactInquiry` |
| **Table** | `jobs_contactinquiry` |
| **Purpose** | Public contact form submissions (no User FK) |
| **Meta** | ordering `-received_at` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| name | CharField(100) | name | required | — | — | — | Submitter name |
| email | EmailField | email | required | — | — | — | Contact email |
| topic | CharField(40) | topic | required | — | TOPIC_CHOICES | — | Topic |
| message | TextField(5000) | message | required | — | — | — | Message body |
| received_at | DateTimeField | received_at | auto | — | auto_now_add | — | Received time |

**TOPIC_CHOICES:** General question, Account support, Job seeker support, Employer support.

---

## 9. SavedJob

| | |
| --- | --- |
| **Model** | `SavedJob` |
| **Table** | `jobs_savedjob` |
| **Purpose** | Job bookmark by seeker |
| **Meta** | UniqueConstraint `(user, job)`; ordering `-saved_at` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| user | ForeignKey | user_id | required | FK | — | → User CASCADE `saved_jobs` | Saver |
| job | ForeignKey | job_id | required | FK | — | → Job CASCADE `saved_by` | Saved job |
| saved_at | DateTimeField | saved_at | auto | — | auto_now_add | — | Bookmark time |

---

## 10. Notification

| | |
| --- | --- |
| **Model** | `Notification` |
| **Table** | `jobs_notification` |
| **Purpose** | In-app user notification |
| **Meta** | ordering `-created_at` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| user | ForeignKey | user_id | required | FK | — | → User CASCADE `portal_notifications` | Recipient |
| title | CharField(160) | title | required | — | — | — | Title |
| message | TextField(2000) | message | required | — | — | — | Body |
| target_url | CharField(500) | target_url | blank OK | — | `''` | — | Optional deep link |
| category | CharField(20) | category | blank OK | — | `general` / CATEGORY_CHOICES | — | Category |
| is_read | BooleanField | is_read | required | — | `False` | — | Read flag |
| created_at | DateTimeField | created_at | auto | — | auto_now_add | — | Created |

**CATEGORY_CHOICES:** application, interview, job_alert, account, general.

---

## 11. JobAlertPreference

| | |
| --- | --- |
| **Model** | `JobAlertPreference` |
| **Table** | `jobs_jobalertpreference` |
| **Purpose** | Saved search criteria for job alerts |
| **Meta** | ordering `-updated_at` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| user | ForeignKey | user_id | required | FK | — | → User CASCADE `job_alert_preferences` | Owner |
| title | CharField(100) | title | blank OK | — | `''` | — | Preferred title keywords |
| location | CharField(100) | location | blank OK | — | `''` | — | Preferred location |
| skills | CharField(200) | skills | blank OK | — | `''` | — | Preferred skills string |
| job_type | CharField(20) | job_type | blank OK | — | Job.JOB_TYPE_CHOICES | — | Preferred type |
| work_mode | CharField(20) | work_mode | blank OK | — | On-site\|Hybrid\|Remote | — | Preferred mode |
| experience | CharField(100) | experience | blank OK | — | `''` | — | Preferred experience text |
| enabled | BooleanField | enabled | required | — | `True` | — | Alerts on/off |
| created_at | DateTimeField | created_at | auto | — | auto_now_add | — | Created |
| updated_at | DateTimeField | updated_at | auto | — | auto_now | — | Updated |

---

## 12. JobAlert

| | |
| --- | --- |
| **Model** | `JobAlert` |
| **Table** | `jobs_jobalert` |
| **Purpose** | Unique match notification between user and job |
| **Meta** | UniqueConstraint `(user, job)`; ordering `-created_at` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| user | ForeignKey | user_id | required | FK | — | → User CASCADE `job_alerts` | Recipient |
| job | ForeignKey | job_id | required | FK | — | → Job CASCADE `alerts` | Matched job |
| preference | ForeignKey | preference_id | null/blank OK | FK | — | → JobAlertPreference SET_NULL `matches` | Source preference |
| matched_fields | JSONField | matched_fields | blank OK | — | `list` callable | — | Which criteria matched |
| created_at | DateTimeField | created_at | auto | — | auto_now_add | — | Created |

---

## 13. Interview

| | |
| --- | --- |
| **Model** | `Interview` |
| **Table** | `jobs_interview` |
| **Purpose** | Interview appointment for an application |
| **Meta** | UniqueConstraint `(application, scheduled_at)`; ordering `scheduled_at` |

### Fields

| Field | Django Type | Database Column | Required / Nullable | Unique / Indexed | Default / Choices | Relationship | Description |
| --- | --- | --- | --- | --- | --- | --- | --- |
| id | BigAutoField | id | PK | PK | auto | — | Primary key |
| application | ForeignKey | application_id | required | FK | — | → Application CASCADE `interviews` | Linked application |
| scheduled_at | DateTimeField | scheduled_at | required | — | — | — | Schedule instant |
| location_or_link | CharField(500) | location_or_link | blank OK | — | `''` | — | Place or meeting URL |
| notes | TextField(3000) | notes | blank OK | — | `''` | — | Notes |
| status | CharField(20) | status | required | — | `scheduled` / scheduled\|completed\|cancelled | — | Interview status |
| created_by | ForeignKey | created_by_id | **null OK** (blank default False) | FK | — | → User SET_NULL `created_interviews` | Creator |
| created_at | DateTimeField | created_at | auto | — | auto_now_add | — | Created |

Note: `created_by` allows `null=True` without `blank=True` in model — forms may need care (**integrity observation**).

---

## Duplicate and overlapping concepts

| ID | A | B | Why overlap | Classification | Confidence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | `Profile.skills` | `Job.skills` / `JobAlertPreference.skills` | Free-text skill bags, no Skill entity | OVERLAPPING CONCEPT | High | Future normalize only with approved migration |
| D2 | `Profile.experience` | `Job.experience` / alert preference | Same free-text pattern | OVERLAPPING CONCEPT | High | Keep separate meanings (candidate vs requirement) unless product unifies |
| D3 | `Profile.location` | `Company.location` / `Job.location` | Repeated location strings | OVERLAPPING CONCEPT | High | Optional Location entity later |
| D4 | `Profile.role` | `SignupRecord.role` | Both store seeker/employer role | POSSIBLE DUPLICATE | Medium | Document which is authoritative at runtime (Profile used in dashboards) |
| D5 | `Profile.resume` FileField | `ResumeDraft.content` JSON | Two resume representations | INTENTIONALLY SEPARATE | High | Keep; clarify product roles in docs |
| D6 | `User.email` | `SignupRecord.email` | Email stored twice | OVERLAPPING CONCEPT | High | Keep audit trail; ensure sync on change |
| D7 | Application statuses new vs `pending`/`reviewed` | Same field | Dual vocabulary | OVERLAPPING CONCEPT | High | Migrate/normalize statuses in future approved change |
| D8 | `Notification` | (no preference model) | Preferences absent | NEEDS MANUAL REVIEW | Low | Optional NotificationPreference later |
| D9 | `Company.owner` O2O | (no CompanyMember) | Single-owner only | INTENTIONALLY SEPARATE / gap | High | CompanyMember only if multi-recruiter required |

**No CONFIRMED DUPLICATE tables** (no two models storing identical row-level entities).

---

## Model ↔ database comparison

| Check | Result |
| --- | --- |
| Every `jobs_*` model table exists in SQLite | **Yes** |
| Extra `jobs_*` tables without models | **None** |
| Column set mismatches (model concrete cols vs PRAGMA) | **None** |
| Migrations vs models (Day 5) | `jobs` 0001–0014 applied; 0 unapplied |

Third-party tables (`auth_*`, `account_*`, `socialaccount_*`, `django_*`) exist and are expected.

---

## Data integrity observations

| ID | Model / field | Evidence | Impact | Suggested correction | Migration later? | Approval? |
| --- | --- | --- | --- | --- | --- | --- |
| I1 | Company.owner SET_NULL | models.py | Orphan companies after user delete | Policy: reassign or PROTECT | Yes | Yes |
| I2 | CASCADE Job→Application→… | models.py | Wide deletes | Document; soft-delete if needed | Maybe | Yes |
| I3 | Application dual statuses | STATUS_CHOICES | Filter bugs | Data migration to single set | Yes | Yes |
| I4 | No Meta indexes on Job.is_active / Notification.is_read | Meta empty indexes | Slower lists at scale | Additive indexes | Yes | Yes |
| I5 | Interview.created_by null without blank | Field def | Admin/form quirks | Align null/blank | Small | Yes |
| I6 | String skills | CharFields | No referential integrity | Skill M2M phased plan | Yes | Yes |
| I7 | ResumeDraft / StatusEvent not in admin | admin.py | Ops visibility | Register admins | No schema | Optional |

---

## Future migration considerations (not scheduled)

1. Additive indexes only (safest).  
2. Status vocabulary cleanup.  
3. Optional Skill / Education / Experience / CompanyMember entities — **require Day approval + backup** (Day 5 backup exists).  
4. Do **not** squash 0001–0014 without a dedicated plan.

---

## Progress note (Day 7)

Inspected `jobs/models.py` and Django `_meta` for all 13 concrete models (103 fields, 18 relationships). Compared tables/columns to live SQLite read-only. Produced ERD + this dictionary. No migrations, no model edits, no record changes. Unverified: runtime private record contents (intentionally not inspected). Day 8 not started.
