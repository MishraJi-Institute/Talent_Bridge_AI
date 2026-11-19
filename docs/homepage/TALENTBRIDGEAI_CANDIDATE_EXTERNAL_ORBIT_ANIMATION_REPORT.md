# TalentBridgeAI Candidate External Orbit Animation Report

## Goal
Orbit candidate avatars OUTSIDE the main profile card, then approach centre + zoom.

## Implementation
- JS: frontend/js/core/tb-match-score.js (orbitMetrics uses profile card bounding circle + clearance)
- CSS: frontend/css/pages/tb-hero-visuals.css (overflow visible, larger scene padding, orbit layering)
- Flyer approach element for outside-to-centre travel
- Prompt: docs/homepage/TALENTBRIDGEAI_EXTERNAL_ORBIT_PROMPT.md

## Timing
- Orbit ~15s
- Approach ~1000ms
- Zoom in ~2800ms / out ~2000ms / peak ~1.28

## Verification
- Local code updated to orbit-ext2
- Live Pages may still show older bundle until redeploy push
- Prefer verifying on Django :8000 after restart, or after Actions deploy of this commit

## Remaining
- Confirm visually that no avatar sits inside the white profile card after redeploy
- Capture dedicated approach-phase screenshot after redeploy
