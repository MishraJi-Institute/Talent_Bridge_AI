# TalentBridgeAI Candidate Matching Animation Report

**Date:** 2026-11-18  
**Scope:** Homepage hero AI matching showcase (demo profiles) + portrait crop correction  
**Project root:** `E:\Job POrtal\TalentBridgeAI`  
**Server:** Django on port **8000**  
**Git:** No `.git` in workspace  

---

## Candidate data structure

Single source of truth in `frontend/js/core/tb-match-score.js` (`CANDIDATES` array).

Each profile object:

| Field | Purpose |
|-------|---------|
| `name`, `role` | Identity |
| `skills`, `experience`, `education`, `softSkills` | Attribute rows |
| `chips` | AI matching chip labels |
| `score`, `fitLabel` | Match score + category |
| `image`, `alt` | Local portrait + accessible alt text |

**Profiles implemented: 5** (demo only — not live users / not live AI).

| # | Name | Role | Score | Image |
|---|------|------|-------|-------|
| 1 | Rahil Sharma | Python Developer | 98% | `/images/tb-match-rahil.jpg` |
| 2 | Ananya Verma | Data Scientist | 94% | `/images/tb-match-ananya.jpg` |
| 3 | Arjun Mehta | Full Stack Developer | 91% | `/images/tb-match-arjun.jpg` |
| 4 | Priya Singh | UI/UX Designer | 96% | `/images/tb-match-priya.jpg` |
| 5 | Karan Patel | Cloud Engineer | 93% | `/images/tb-match-karan.jpg` |

DEMO disclosure retained in `.tb-match-note` and result card (“DEMO · illustrative only”).

---

## Image sources and verification

| Asset | Source | HTTP | Dimensions |
|-------|--------|------|------------|
| `tb-match-rahil.jpg` | Existing hero candidate asset (copied) | 200 | 1024×682 (~1.50) |
| `tb-match-ananya.jpg` | Unsplash (same source used elsewhere on homepage), cached locally | 200 | 640×480 |
| `tb-match-arjun.jpg` | **Replaced 2026-11-18** — Pexels stock portrait (licensed), local file | 200 | 640×480 |
| `tb-match-priya.jpg` | Unsplash, cached locally | 200 | 640×480 |
| `tb-match-karan.jpg` | Unsplash, cached locally | 200 | 640×480 |

Images are illustrative stock portraits, not registered TalentBridge users.

### Arjun Mehta portrait replacement (follow-up)

**Goal:** Replace only Arjun Mehta’s photo with a distinct professional Indian male developer portrait (≈25–35, business-casual).

| Item | Result |
|------|--------|
| Data entry | `CANDIDATES[2]` in `tb-match-score.js` — name/role/skills/experience/education/softSkills/chips/**91%** unchanged |
| Mapping | `image: "/images/tb-match-arjun.jpg?v=3"` |
| Asset file | `frontend/assets/images/tb-match-arjun.jpg` (62,105 bytes, 640×480) |
| Subject | South Asian male, friendly smile, blue crew-neck tee, arms crossed, white brick background |
| Uniqueness | SHA-256 prefix `72F57E84CFC7` — distinct from Rahil / Ananya / Priya / Karan hashes |
| Other candidates | Image paths and files untouched |
| Animation / layout | HOLD 4500 / FADE 520 / score 900 / carousel order unchanged |

**Browser verification (live `http://127.0.0.1:8000/`):**

1. Forced Arjun via demo dot → card showed **Arjun Mehta · Full Stack Developer · React/Node/PostgreSQL · 91% · Great fit**.
2. Portrait URL `tb-match-arjun.jpg?v=3` loaded (`complete`, natural **640×480**), HTTP **200**.
3. CSS: `object-fit: contain`, photo frame ratio **1.333 (4/3)** — full source visible, no stretch.
4. Visual check: new blue-tee / brick portrait; not Rahil (blazer/office) or Karan (studio sweater).
5. Transition out: Arjun → Priya — `is-transitioning` observed mid-fade; after settle Priya **96%** and `tb-match-priya.jpg?v=2`.

**Not changed:** Django, other candidate images, carousel timing, 98% Rahil score animation, homepage redesign.

---

## Portrait crop correction (follow-up)

### Root cause
1. `.tb-match-profile__photo` used a **fixed short height** (128px / 160px) with `overflow: hidden`.
2. Image used **`object-fit: cover`** + `object-position: center 18%`.
3. `tb-homepage-coherence.css` also forced **cover** on `.tb-match-profile__photo img`.
4. Initial Unsplash downloads used aggressive `fit=crop` landscape crops that already cut heads in the **source files**.

Together, portraits lost faces/heads.

### Fix
- Photo frame uses **`aspect-ratio: 4 / 3`** matching refreshed assets.
- Image uses **`object-fit: contain`** + **`object-position: center center`**.
- Soft fill background `#e8eef8` for any letterboxing (e.g. Rahil ~1.50 source).
- Coherence override forces contain for match portraits only.
- Re-downloaded Ananya/Arjun/Priya/Karan as **640×480 face-safe** crops (`crop=faces`).
- Mobile no longer forces a fixed photo height.

### CDP verification (portrait fit)

| Viewport | object-fit | Box ratio | Result |
|----------|------------|-----------|--------|
| 1440 | `contain` | 1.333 (4/3) | Matches 640×480 assets; full source visible |
| 375 | `contain` | 4/3 | No page overflow |
| Other listed widths | CSS rules applied | 4/3 | Same strategy |

Evidence: `docs/evidence/homepage-hero-correction-20261118/after-portrait-contain-1440-scene.png`

---

## Animation timing

| Phase | Duration |
|-------|----------|
| Hold per candidate | 4500 ms |
| Fade out / fade in | 520 ms each |
| Score ring tween | 900 ms (easeOutCubic) |

Transitions update **one candidate object at a time** (image + all fields + chips + score together).  
Dots allow manual selection; hold timer restarts after selection.  
`prefers-reduced-motion: reduce` → static first profile, no autoplay / no fade.

---

## Match score synchronization

- Ring `stroke-dashoffset` and count animate from previous score → next score.
- `data-score` and result `aria-label` update with the active candidate.
- Ring remains 84×84 with `overflow: hidden` (prior alignment fix preserved).

---

## Files changed

| File | Change |
|------|--------|
| `frontend/index.html` | Showcase markup (identity, data fields, dots); CSS/JS cache bumps |
| `frontend/js/core/tb-match-score.js` | 5-candidate showcase controller |
| `frontend/css/pages/tb-homepage.css` | Identity, dots, transitions; **portrait contain + aspect-ratio** |
| `frontend/css/pages/tb-homepage-coherence.css` | Match photo contain override |
| `frontend/assets/images/tb-match-*.jpg` | Local demo portraits |
| `docs/homepage/TALENTBRIDGEAI_CANDIDATE_MATCHING_ANIMATION_REPORT.md` | This report |

**Not changed:** Django models, migrations, auth, search, other homepage sections.

---

## Browser verification results

- Port **8000**; CSS `hero31` / `coh5` confirmed loaded.
- All 5 local portrait assets HTTP **200**.
- Dots present for all 5 candidates; manual selection updates profile fields.
- Measured `object-fit: contain` and matching `7 / 4` frame on desktop and mobile.
- DEMO note visible.
- No horizontal overflow measured at 1440 / 375.

### Remaining limitations

1. Rapid manual clicking during a fade can leave score mid-tween until the next settle (busy lock). Normal autoplay / single selection is fine.
2. Rahil’s source ratio (~1.50) may show slim letterboxing in the 7:4 frame by design (full image still visible).
3. Portraits are licensed stock / demo assets — not real platform candidates.

---

**STOP.** Arjun Mehta image replacement only — awaiting user approval.
