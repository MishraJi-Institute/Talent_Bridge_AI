# TalentBridgeAI — Candidate Cinematic Animation & Visuals Balance Report

**Date:** 2026-11-19  
**Scope:** (1) AI Matching Visuals section balance · (2) Hero showcase Ken Burns photo zoom  
**Project root:** `E:\Job POrtal\TalentBridgeAI`  
**Server:** Django `:8000`  
**Git:** CLI not available in this environment  

---

## Empty-space issues identified

| Issue | Cause |
|-------|--------|
| Sparse visuals section | Intro stacked above a wide 2-card grid → large unused horizontal/vertical bands |
| Tall section height | Large `min-height` on viz cards + vertical stacking of intro + grid |
| Weak left/right relationship | Copy and visualizations not composed as one unit |

---

## AI Matching Visuals layout improvements

- Rebuilt section as a **two-column composition**:
  - **Left:** badge, heading, lead, 3 purposeful matching benefit rows, demo disclosure
  - **Right:** AI Talent Network + Smart Matching cards in a paired stage
- Desktop stage uses **side-by-side** equal cards (`grid-template-columns: 1fr 1fr`)
- Reduced section padding; aligned card radius/shadow/label treatment
- Strengthened AI core / matching target prominence
- Stacks cleanly below ~900–1100px

### Follow-up size correction (same day)

**Why cards looked too small:** height was capped at **360px**, and `minmax(380px, 1fr)` on the stage could overflow/clip the second card.

**New desktop dimensions (measured 1440px):**
| Card | Width | Height |
|------|-------|--------|
| AI Talent Network | **418px** | **520px** |
| Smart Matching | **418px** | **520px** |

Layout: left copy `~300px` | right stage `1fr 1fr` with larger globe/target (~340px) and bigger orbit avatars. Internal illustrations scaled up with the cards.

---

## Candidate image zoom implementation

Unified candidate objects in `tb-match-score.js` (same array; added `id`, `objectPosition`, `zoomOrigin`).

### Sequence (photo element only)
1. Candidate data + score applied together at **scale(1.00)**  
2. **Zoom-IN** to **scale(1.20)** over **2.8s** (WAAPI, ease-in-out)  
3. **Zoom-OUT** back to **scale(1.00)** over **2.2s**  
4. Brief hold (~0.7s)  
5. Crossfade → next candidate → reset → repeat  

### Timing
| Phase | Value |
|-------|-------|
| Zoom-in | 2800 ms → 1.20× |
| Zoom-out | 2200 ms → 1.00× |
| Hold after zoom | 700 ms |
| Total hold before next | ~5700 ms |
| Fade out / fade in | 650 ms each |
| Score tween | 900 ms (existing) |

### Sync guarantees
- Name, role, skills, experience, education, soft skills, chips, score, ring, image update in one `applyCandidate()` call
- `data-active-candidate` set to candidate `id`
- Per-candidate `--tb-photo-pos` / zoom origin keep faces framed
- Timers cleared on hide / visibility change; zoom animation cancelled on transition

### Reduced motion
- Continuous zoom disabled; stable portrait + normal field updates

---

## Files modified

| File | Change |
|------|--------|
| `frontend/index.html` | Visuals section restructure; cache bumps |
| `frontend/css/pages/tb-hero-visuals.css` | Balanced layout + Ken Burns support styles |
| `frontend/js/core/tb-match-score.js` | WAAPI Ken Burns, timing, sync, focus vars |
| `docs/homepage/TALENTBRIDGEAI_CANDIDATE_CINEMATIC_ANIMATION_REPORT.md` | This report |
| `docs/evidence/cinematic-balance-20261119/` | Screenshots |

**Not changed:** Django models/migrations/auth/URLs/search/job listings/DB stats/other homepage sections.

---

## Browser verification (actual)

URL: `http://127.0.0.1:8000/?fix=3` · viewport **1440×900**

| Check | Result |
|-------|--------|
| Viz cards ≥380×500 | Pass — **418×520** each, both `inView` |
| Equal card heights | Pass |
| No document overflow-x | Pass |
| Zoom-in reaches ~1.20 | Pass — peak measured **1.192** |
| Zoom-out returns ~1.00 | Pass — **1.003** then finished at **1.0** |
| Next candidate sync (image+name+score) | Pass — Rahil 98% → Ananya 94% |
| Ananya continues own zoom-in | Pass — scale grew to **1.177** mid-cycle |
| ≥3 cycles observed | Pass |

### Evidence
- `docs/evidence/cinematic-balance-20261119/01-cinematic-showcase.png`
- `docs/evidence/cinematic-balance-20261119/02-ai-matching-visuals.png`
- `docs/evidence/cinematic-balance-20261119/03-after-large-viz-cards.png`
- `docs/evidence/cinematic-balance-20261119/04-after-zoom-peak-rahil.png`

---

## Remaining limitations

1. When a fixed satellite avatar matches the active carousel candidate, that face can appear twice in the hero scene (demo-only).
2. WAAPI drives the visible zoom (CSS keyframes are fallback only).
3. Below ~1100px the copy stacks above the stage; below ~900px the two viz cards stack.
4. Git status unavailable without `git` on PATH.

---

**STOP.** Awaiting approval. Day 11 not started.
