# Apple-Design White Theme for HTML PPT

## Description
White-background, Apple-keynote inspired theme with animations and interactions.
Used for: corporate presentations, course proposals, client-facing decks.

## Key Design Tokens
```css
:root {
  --bg: #ffffff;
  --bg-subtle: #f5f5f7;
  --bg-card: #ffffff;
  --ink: #1d1d1f;
  --ink-2: #515154;
  --ink-3: #86868b;
  --ink-4: #d2d2d7;
  --blue: #0071e3;
  --green: #34c759;
  --orange: #ff9500;
  --red: #ff3b30;
  --purple: #af52de;
  --shadow: 0 2px 12px rgba(0,0,0,0.06);
  --shadow-lg: 0 8px 30px rgba(0,0,0,0.08);
  --radius: 20px;
}
```

## Animation System
- `fadeUp`: translateY(30px) → 0, 0.7s cubic-bezier(0.22,1,0.36,1)
- `fadeIn`: opacity 0→1, 0.6s ease
- `scaleIn`: scale(0.92)→1, 0.6s cubic-bezier
- `slideRight`: translateX(-30px)→0, 0.6s cubic-bezier
- Delay classes: `.d1` through `.d8` (0.1s increments)
- Trigger: add `.anim.a-up.d1` to elements, animation fires on `.slide.active`

## Interactive Elements
- Cards: hover → translateY(-4px) + shadow increase
- Timeline rows: hover → background change to accent-light
- Progress bar: top-fixed, width = (current/total * 100)%
- Nav dots: bottom-center, active = wider pill shape

## Typography Scale
- Hero: 4rem/900 weight
- Section: 2.8rem/800
- Module: 2rem/700
- Body: 1.1rem/400, color var(--ink-2)
- Label: 0.82rem/700, uppercase, letter-spacing 0.12em

## Slide Structure (12-page corporate deck)
1. Cover: title + 4 stats
2. Why: 3 pain points + key insight
3. For Whom: 2-column (研发/管理) + principles
4. Design Philosophy: 6 cards in 3-col grid
5. Overview: 2-column day breakdown with pills
6. Day 1 Detail: timeline with tags
7. Day 2 Detail: timeline with highlighted modules
8. Methodology: 4-step closed loop
9. Deliverables: 6 cards in 3-col grid
10. Case Studies: 5 products + 2 contrasting cards
11. Stability: 2-column (stable/iterable)
12. CTA: centered with decorative circles

## Keyboard/Touch
- ← → Space PgDn: next
- ← ↑ PgUp: previous
- Home/End: first/last
- F: fullscreen
- Click left/right half: prev/next
- Touch swipe: prev/next
