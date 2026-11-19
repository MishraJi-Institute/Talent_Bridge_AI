# TalentBridgeAI — Day 12 Proposed Folder Structure

**Prepared:** 2026-11-19 (Day 11 deliverable)  
**Status:** PLAN ONLY — **do not execute until user approves Day 12**  
**Basis:** Day 11 dependency map + live `settings.py` / `urls.py` / tools / junctions

---

## 1. Guiding principles

1. Prefer organizing **inside** already-wired trees (`frontend/`, `backend/legacy-django/`, `docs/`, `scripts/`) over inventing duplicate root `templates/` or `static/` that fight Django settings.
2. Preserve Windows **compatibility junctions** until every script and doc uses `frontend/` / `backend/` paths.
3. Never move `.env`, `database/`, or `private_media/` without a dedicated settings + backup rehearsal.
4. Install **Git** before Day 12 if possible; commit after each safe move group.
5. Restore point already exists:  
   `E:\Job POrtal\TalentBridgeAI_Day11_PreOrganization_Backup_2026-11-19_08-38-38`

---

## 2. Proposed target shape (conceptual)

```text
TalentBridgeAI/                          # KEEP root
├── .env / .env.example                  # KEEP
├── .gitignore / README.md / netlify.toml / workspace
├── .vscode/ .github/
├── frontend/                            # KEEP (canonical UI sources)
│   ├── index.html
│   ├── pages/
│   ├── css/
│   ├── js/
│   └── assets/images/ …
├── backend/
│   └── legacy-django/                   # KEEP Django project
│       ├── config/
│       ├── jobs/
│       ├── templates/                   # Django-only templates (already here)
│       ├── static/
│       └── manage.py
├── database/                            # KEEP
├── private_media/                       # KEEP
├── docs/                                # KEEP; may tidy subfolders
├── scripts/                             # KEEP; may tidy subfolders
├── tools/                               # KEEP
├── tests/                               # KEEP or document → jobs tests
├── site/                                # GENERATED only
├── backups/ logs/ releases/             # KEEP runtime/ops
└── css js images pages legacy-django    # KEEP junctions (Phase A)
```

**Do not** create a second root-level `templates/` or `static/` that duplicates `frontend/` unless `TEMPLATES` / `STATICFILES_DIRS` are rewritten in the same PR.

---

## 3. File-to-destination mapping (candidates)

| Item | Move on Day 12? | Proposed destination | Notes |
|------|-----------------|----------------------|-------|
| `.env`, `.env.example` | **No** | Remain root | Runtime contract |
| `database/`, `private_media/` | **No** | Remain root | settings paths |
| `tools/`, `netlify.toml` | **No** | Remain root | Build/lifecycle |
| `frontend/**` | **No wholesale move** | Stay under `frontend/` | Optional internal tidy only |
| `backend/legacy-django/**` | **No wholesale move** | Stay | Optional internal tidy only |
| Root junctions | **No (Phase A)** | Keep | Remove only in a later phase after ref audit |
| `docs/audit/*` | Optional tidy | `docs/audit/dayN/…` already used | Low risk |
| Loose docs at odd paths | Optional | Align under `docs/{setup,architecture,…}` | Update README links |
| `scripts/*.bat` wrappers if any remain at root | Optional | `scripts/startup|install|…` | Update README/`index.html` |
| `site/` | Rebuild only | Stay generated | Never hand-edit |
| Root `tests/` | Optional docs merge | Keep or point README to `jobs` tests | Low risk |
| `requirements.txt` | Already under Django dir | Keep `backend/legacy-django/requirements.txt` | Do not invent conflicting root copy without need |

---

## 4. Files that must remain in the root

- `.env`, `.env.example`, `.gitignore`, `.gitattributes`
- `README.md`, `netlify.toml`, `TalentBridgeAI.code-workspace`
- `.vscode/`, `.github/`
- `database/`, `private_media/`
- `tools/`
- Runtime: `.talentbridge_django.*` (generated)
- Compatibility junctions until explicitly retired

---

## 5. Required reference updates (if any move proceeds)

| Change class | Update these |
|--------------|--------------|
| Any script path change | Matching `.bat`/`.ps1`, README, `index.html` stub text |
| Frontend internal folder rename | `settings.STATICFILES_DIRS`, `TEMPLATES`, `urls.PAGES`, `build_static.py`, HTML asset URLs |
| Removing a junction | Confirm no BAT uses root `css\`/`js\`/`pages\`; recreate or update |
| Moving `tools/build_static.py` | `netlify.toml`, release scripts |
| Moving `database/` | `settings.py` DB path + backup scripts + installer preserve lists |

---

## 6. Suggested Day 12 order (only after approval)

### Phase A — Safety first (no structural moves)

1. Install Git (if still missing); `git init` or connect remote.  
2. Branch from Day 11 tree: e.g. `chore/day12-organization`.  
3. Commit current homepage/animation work.  
4. Re-verify backup path still valid.

### Phase B — Documentation-only organization (lowest risk)

1. Ensure all Day 11/Phase 1 reports sit under `docs/audit/…`.  
2. Fix broken doc links in README if any.  
3. `manage.py check` + homepage HTTP smoke.

### Phase C — Scripts clarity (medium risk)

1. Confirm every root-facing BAT lives under `scripts/{install,startup,…}`.  
2. Update README / stub `index.html` references.  
3. Run `START_TALENTBRIDGEAI.bat` health paths.

### Phase D — Frontend internal tidy only if needed (high caution)

1. Do **not** move `frontend/` off root.  
2. If renaming CSS/JS subfolders, update HTML cache-bust links + static dirs in one commit.  
3. Visual check: homepage orbit + AI Matching Visuals.

### Phase E — Junction retirement (defer unless necessary)

1. Full ripgrep for root `\\css\\`, `/css/`, `pages\\`, `legacy-django\\`.  
2. Only then remove junctions.

**Avoid on Day 12:** moving Django `jobs` app, renaming `config`, rewriting `BASE_DIR`, deleting migrations, touching `.env` secrets, stopping DB, removing junctions without audit.

---

## 7. Testing plan after each group

| After | Tests |
|-------|-------|
| Any phase | `manage.py check` |
| Scripts phase | Lifecycle start health (or CHECK_DJANGO_SERVER.bat) without killing a healthy managed server blindly |
| Frontend phase | Homepage `/` 200; orbit nodes visible; `/css/...` `/js/...` 200 |
| Docs-only | Link spot-check README |
| Before merge | `manage.py test jobs` (expect known 2 failures from Day 10 unless fixed separately) |

---

## 8. Risk warnings

- **Homepage animation work is recent and valuable** — treat `frontend/js/core/tb-match-score.js` and `tb-hero-visuals.css` as freeze-critical during moves.  
- **Dual layout support** (`legacy-django` junction + `backend/legacy-django`) is intentional; do not delete one side casually.  
- **No Git today** — without commits, Day 12 moves are harder to reverse; use the Day 11 sibling backup and prefer small steps.  
- Do not restore the Day 11 backup **over** the live tree without an explicit recovery drill in a separate folder.

---

## 9. Explicit non-goals for Day 12 (unless newly approved)

- Day 13+ feature work  
- Database engine migration  
- OAuth redesign  
- Fixing the two known jobs test failures (track separately)  
- Full “Django textbook” root `templates/` + `static/` redesign that ignores current hybrid layout
