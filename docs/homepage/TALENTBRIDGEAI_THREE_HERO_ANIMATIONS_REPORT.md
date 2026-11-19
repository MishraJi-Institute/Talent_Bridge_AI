# TalentBridgeAI — Three Hero Animations Report

**Date:** 2026-11-19  
**Scope:** Three selected hero visualizations only (no Day 11, no unrelated redesign)  
**Project root:** `E:\Job POrtal\TalentBridgeAI`  
**Server:** Django on port **8000**  
**Git:** `git` CLI not available in this environment (no status collected)

---

## Selected visualizations

| # | Concept | Placement |
|---|---------|-----------|
| 1 | Candidate team showcase (central portrait + surrounding profiles) | Enhanced existing hero `.tb-match-scene` |
| 2 | Dark AI network globe + orbiting candidate nodes | New section `.tb-hero-visuals` → `.tb-viz--network` |
| 3 | Light smart-matching target + orbiting avatars | New section `.tb-hero-visuals` → `.tb-viz--target` |

Existing candidate carousel (`tb-match-score.js`) is **reused** for the central team showcase identity/score — not duplicated as a second matching engine.

---

## Animation techniques

### 1) Team showcase
- Main photo: CSS `tb-main-float` (~4.4s ease-in-out)
- Profile card: entrance `tb-team-enter` (0.7s)
- Satellite cards: independent `tb-sat-drift` (4.2–5.4s, staggered delays)
- AI badge: `tb-badge-pulse` + AI core soft shadow pulse
- SVG energy rings: scale/opacity pulse
- Match score counting remains from existing `tb-match-score.js`

### 2) AI network globe
- Wireframe SVG globe inside `.tb-globe-spin` rotating **36s linear**
- Dashed latitude paths: `tb-dash-flow` (~3.2s)
- AI core: `tb-core-breathe` (~3.4s)
- Candidate nodes on dual CSS orbits (**18s** / **26s reverse**) with counter-rotation so faces stay upright
- Network point pulses on peripheral dots

### 3) Smart matching target
- Concentric SVG rings with pulse
- Central match icon + success check pop
- Connection path dash flow + light particles
- Dual orbits (**16s** / **22s reverse**) with 5 demo avatars
- Counter-rotation keeps portraits upright

### Runtime control
- `tb-hero-visuals.js` uses `IntersectionObserver` to toggle `.is-paused` when panels leave the viewport
- `prefers-reduced-motion: reduce` disables continuous orbits/rotation/float while keeping a stable composition

---

## Timing (implemented)

| Element | Duration |
|---------|----------|
| Main candidate float | ~4.4s |
| Satellite drift | ~4.2–5.4s |
| Globe rotation | 36s |
| Network orbits | 18s / 26s |
| AI core / target pulse | ~3.4–4.0s |
| Target orbits | 16s / 22s |
| Connection dash / particles | ~2.8–3.2s |

---

## Image sources

Illustrative local demo portraits (not live users):

| Asset | Used in |
|-------|---------|
| `/images/tb-match-rahil.jpg?v=2` | Showcase rotation + network/target nodes |
| `/images/tb-match-ananya.jpg?v=2` | Satellites + nodes |
| `/images/tb-match-arjun.jpg?v=3` | Satellites + nodes |
| `/images/tb-match-priya.jpg?v=2` | Satellites + nodes |
| `/images/tb-match-karan.jpg?v=2` | Satellites + nodes |

Portrait presentation: `object-fit: contain` with centered position for showcase/satellites/orbit avatars (override against hero-wide `cover` rule).

---

## Files changed

| File | Change |
|------|--------|
| `frontend/index.html` | Satellites + rings on match scene; new visuals section; CSS/JS links |
| `frontend/css/pages/tb-hero-visuals.css` | **New** — all three motion systems + responsive + reduced-motion |
| `frontend/js/core/tb-hero-visuals.js` | **New** — IntersectionObserver pause helper |
| `docs/homepage/TALENTBRIDGEAI_THREE_HERO_ANIMATIONS_REPORT.md` | This report |
| `docs/evidence/three-hero-animations-20261119/*.png` | Browser evidence screenshots |

**Not changed:** Django models, migrations, auth, URLs, search, job listings, DB stats, other homepage marketing sections (aside from inserting the visuals section after the hero).

---

## Browser verification (actual)

Live URL: `http://127.0.0.1:8000/?viz=2`

| Check | Result |
|-------|--------|
| CSS/JS HTTP 200 | Pass (`tb-hero-visuals.css?v=20261119-viz2`, `.js`) |
| Team float motion (transform samples ~2.5s apart) | Pass — `photoMoved: true` |
| Globe rotation | Pass — `globeMoved: true` |
| Target orbit | Pass — `orbitMoved: true` |
| AI core breathe | Pass — `coreMoved: true` |
| Portrait loads | Pass for match + orbit assets (HTTP 200; contain fit confirmed) |
| Horizontal overflow | None measured |
| Mobile 390 | Network + stacked layout OK; satellites hidden ≤430px by design |
| Reduced motion | CSS disables continuous animations |

Observed each visualization with timed transform sampling (~2.5s intervals across team / network / target). Continuous motion confirmed via matrix deltas.

### Evidence screenshots

- `docs/evidence/three-hero-animations-20261119/01-team-showcase.png`
- `docs/evidence/three-hero-animations-20261119/02-ai-network-globe.png`
- `docs/evidence/three-hero-animations-20261119/03-smart-matching-target.png`

---

## Performance observations

- Motion is CSS-transform/opacity based (compositor-friendly)
- No animation libraries; no GIF/video for these three concepts
- Off-screen panels pause via `is-paused`
- No extra continuous JS timers beyond IntersectionObserver

---

## Remaining limitations

1. When the rotating central showcase shows the same person as a fixed satellite (e.g. Arjun), that face can appear twice briefly — demo-only.
2. On very narrow screens, team satellites are hidden to protect layout; float + AI pulse remain.
3. Globe is an SVG wireframe network sphere (digital AI globe), not a photoreal Earth texture — intentional for brand/performance.
4. Paint reference image with red marks was not found as a distinct asset in the Cursor assets folder; implementation followed the three written concept specs.
5. Git CLI unavailable here — commit status not verified.

---

**STOP.** Awaiting approval. Day 11 not started.
