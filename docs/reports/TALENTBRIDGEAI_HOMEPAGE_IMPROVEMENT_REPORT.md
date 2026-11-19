# TalentBridgeAI — Homepage Improvement Report

Date: 2026-11-18

## Approach

Improved the existing Django-rendered `index.html` homepage. Did **not** rebuild from scratch. Live counts, routes, forms, and DEMO DATA disclosures preserved.

## Visual / UX changes

- Light premium elevation CSS: `frontend/css/pages/tb-homepage-elevate.css`
- Stronger navy/royal hierarchy, clearer CTA hover lift, frosted stat chips
- Match-scene path dash animation, AI core pulse, signal float (respects `prefers-reduced-motion`)
- Card hover refinement on employer / success sections
- Highlight line “Matched by AI.” kept solid royal blue for readability

## Animation technology

| Piece | Tech | Behavior |
| --- | --- | --- |
| Hero network | Canvas 2D (`tb-hero-network.js`) | Soft drifting nodes + proximity links over light hero |
| Match connectors | CSS stroke-dashoffset | Flowing dashed paths into AI core |
| AI badge / signals | CSS keyframes | Gentle pulse / float |
| Reduced motion | `matchMedia` + CSS media query | Static/low-motion fallback |

No neon glow, no dark-first hero, no gaming effects.

## Cache bust

- `tb-homepage.css?v=20261118-hero9`
- `tb-homepage-attract.css?v=20261118-attract3`
- `tb-homepage-elevate.css?v=20261118-elevate1`
- `tb-hero-network.js?v=20261118-elevate1`
