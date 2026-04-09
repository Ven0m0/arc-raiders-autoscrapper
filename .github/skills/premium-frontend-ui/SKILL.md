---
name: premium-frontend-ui
description: Craft immersive, high-performance premium web experiences with advanced motion, typography, and architectural craftsmanship. Use for award-level landing pages, interactive portfolios, or components requiring top-tier visual polish.
allowed-tools: "Bash, Read, Write, Edit, Glob, Grep"
---

# Premium Frontend UI

Build immersive digital environments that go beyond functional HTML/CSS. Apply these standards for high-end landing pages, interactive portfolios, or specialized components requiring aesthetic excellence.

## Creative Foundations

Choose a strong visual identity before writing layout code:

| Style                 | Characteristics                                                      |
| --------------------- | -------------------------------------------------------------------- |
| **Editorial Brutalism** | High-contrast monochromatic palettes, oversized typography, sharp grids |
| **Organic Fluidity**  | Soft gradients, deep rounded corners, glassmorphism, spring physics  |
| **Cyber / Technical** | Dark mode, neon accents, monospace type, rapid staggered animations  |
| **Cinematic**         | Full-viewport imagery, slow cross-fades, scroll-driven storytelling  |

## Structural Requirements

| Layer                 | Requirement                                                                              |
| --------------------- | ---------------------------------------------------------------------------------------- |
| **Entry sequence**    | Lightweight preloader → fluid transition (split-door, scale-up, or text sweep)          |
| **Hero architecture** | `100vh`/`100dvh` full-bleed, word/char-wrapped headlines for cascade animations          |
| **Navigation**        | Sticky header that hides on scroll-down, reveals on scroll-up; rich hover states         |
| **Typography**        | `clamp()` scale (up to `12vw` headlines), 16-18px body min, variable/premium fonts       |
| **Texture**           | CSS/SVG noise overlay (`mix-blend-mode: overlay`, opacity 0.02-0.05), frosted glass     |

## Motion Design System

| Pattern                 | Implementation                                                                   |
| ----------------------- | -------------------------------------------------------------------------------- |
| **Scroll-driven**       | GSAP ScrollTrigger: pinned containers, horizontal galleries, parallax layers     |
| **Micro-interactions**  | Magnetic buttons (distance-based pull), custom cursor with lerp interpolation    |
| **Dimensional hover**   | CSS `scale`, `rotateX`, `translate3d` for tactile feedback                       |

## Performance Rules

| Rule                         | Detail                                                                    |
| ---------------------------- | ------------------------------------------------------------------------- |
| **Composite only**           | Animate `transform` and `opacity` only — never `width`, `height`, `margin` |
| **will-change**              | Apply before animation, remove after to conserve memory                   |
| **Touch degradation**        | Wrap cursor/hover animations in `@media (hover: hover) and (pointer: fine)` |
| **Reduced motion**           | Wrap heavy animations in `@media (prefers-reduced-motion: no-preference)` |

## Implementation Ecosystem

| Target                  | Libraries                                                              |
| ----------------------- | ---------------------------------------------------------------------- |
| **React/Next.js**     | Framer Motion (springs/layout), Lenis (`@studio-freight/lenis`), React Three Fiber (3D/WebGL) |
| **Vanilla / Astro**     | GSAP (timeline sequencing), Lenis (CDN), SplitType (accessible text chunking) |

## Checklist (Before Delivery)

- [ ] Preloader with fluid transition implemented
- [ ] Hero uses full-bleed layout with animated typography
- [ ] Navigation reacts to scroll direction
- [ ] Animations use only `transform`/`opacity`
- [ ] `@media (prefers-reduced-motion)` guard on heavy animations
- [ ] Touch devices: cursor/hover logic gated with `(hover: hover)` media query
- [ ] Performance: `will-change` added before and removed after animation
