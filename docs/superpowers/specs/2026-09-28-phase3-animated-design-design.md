# Phase 3: Animated Design System — Design Spec

Date: 2026-09-28

## Purpose

Phase 3 of the multi-phase feature expansion (Phase 1: country/category
filters, done. Phase 2: images, not yet built). This phase makes the
existing dark editorial design "heavier" — a real, cohesive motion system
across buttons, tabs, cards, checkboxes, the hero, the navbar, and page
transitions — rather than a scattering of unrelated effects.

Research basis: browsed uiverse.io's open-source button/card library
(explicitly free to reuse — "Copy as HTML/CSS, Tailwind, React and
Figma") for concrete technique ideas: a corner-bracket border reveal, a
sparkle/glow border sweep, and animated gradient pills. None of these are
copied verbatim — every technique below is re-implemented in this
project's own palette (near-black `--bg`, orange `--accent`, Fraunces +
Inter) and re-scaled to fit existing components, not pasted wholesale.

## Design tokens

New CSS custom properties added to `frontend/src/index.css`, alongside
the existing color/spacing tokens:

```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
--dur-fast: 150ms;
--dur-base: 300ms;
--dur-slow: 600ms;
```

All new animations reference these tokens rather than hardcoding
durations/easings, so the whole system's pacing can be tuned in one
place.

## Accessibility: reduced motion

A single `@media (prefers-reduced-motion: reduce)` block near the bottom
of `index.css` disables/shortens every animation and transition added in
this phase (sets durations to near-zero, disables the mouse-follow
spotlight and scroll-reveal). This is a hard requirement for this phase,
not optional polish — a design this animation-heavy needs an escape
hatch for users who've asked their OS to reduce motion.

## Animation inventory

**Buttons** (`index.css` — `.btn`, `.btn-primary`, `.btn-danger`):
- Ghost buttons (`.btn`, `.btn-ghost`): corner-bracket reveal on hover —
  four small corner marks (via `::before`/`::after` on each corner, or a
  single element with clipped corners) that scale/expand into a full
  border outline on hover, adapted from the uiverse.io "Hover me"
  bracket-button technique, recolored to `--accent`.
- Primary button (`.btn-primary`): an animated diagonal shine sweep
  crosses the button on hover (a pseudo-element gradient translated
  across on `:hover`), adapted from uiverse.io's glow-border button
  concept but as a shine sweep instead of a static glow.
- Danger button (`.btn-danger`): a short shake/wiggle keyframe plays on
  hover (a `translateX` keyframe, 2-3 oscillations, ~400ms) as a warning
  cue before the user commits to delete.

**Category tabs** (`CategoryTabs.jsx`/`.css`): an animated pill/underline
element slides between tabs on selection change (measure the active
tab's position/width via a ref and `getBoundingClientRect`, animate a
single absolutely-positioned indicator element's `transform`/`width`
with `--ease-spring`) instead of each tab independently toggling its own
background color.

**Post cards** (`PostCard.jsx`/`.css`, `Home.jsx`):
- Entrance: cards fade+rise in, staggered (each card's animation-delay
  offset by its index), both on initial load and when a card newly
  enters the viewport while scrolling — driven by a single small custom
  hook `useInView` (IntersectionObserver) rather than two separate
  mechanisms for "on load" vs "on scroll."
- Hover: lift (existing `translateY`) plus a glowing accent-colored
  border-shadow.
- **Creative addition:** a cursor-following spotlight — a radial
  gradient positioned at the mouse's coordinates within the card
  (tracked via a `mousemove` handler setting CSS custom properties
  `--mouse-x`/`--mouse-y` consumed by a `background: radial-gradient(...)`
  pseudo-element), giving each card a subtle "light follows your cursor"
  feel on hover. Cheap (no extra dependency, plain CSS custom properties
  + one event handler), and it's the kind of detail that makes a card
  grid feel alive rather than static.

**Country filter checkboxes** (`CountryFilter.jsx`/`.css`): replace the
native `<input type="checkbox">` visually with a custom animated
checkbox — the native input stays for accessibility/functionality
(`opacity: 0`, still focusable and clickable) but a sibling element
draws a custom box + checkmark, with the checkmark path animating in via
`stroke-dashoffset` when checked (classic SVG checkmark-draw technique).

**Loading state** (`Home.jsx`/`Home.css`): replace the plain "Loading
posts…" text with pulsing skeleton card placeholders (shimmering
gradient sweep across gray boxes shaped like `PostCard`), matching the
grid layout so the transition from skeleton to real cards doesn't jump.

**Post form** (`PostForm.jsx`/`.css`): **creative addition** — on
successful submit, before `onSubmit`'s navigation fires, briefly show a
checkmark pulse animation over/replacing the submit button (a small
`scale`+`opacity` keyframe on a checkmark icon) as positive feedback,
rather than the button just silently going away on navigation.

**Hero** (`Home.jsx`/`Home.css`):
- Headline animates in staggered by word (split into `<span>`s per word,
  each fades+rises in with an incremental delay) on page load.
- **Creative addition:** a slow-drifting animated gradient backdrop
  behind the hero (large, soft, low-opacity blurred shapes in `--accent`
  and a secondary muted tone, animated via `transform: translate` on a
  long `ease-in-out` loop) — adds depth without competing with the text.
- **Creative addition:** an accent-colored underline sweeps in beneath
  the headline after the word-stagger completes (a `::after` element
  animating `width` from 0 to 100%).

**Navbar** (`Navbar.jsx`/`.css`): shrinks slightly (reduced padding,
smaller brand text) once the page is scrolled past a small threshold,
animated via a scroll listener toggling a class, transitioning smoothly
via the existing `transition` properties already on `.navbar`.

**Page transitions** (`App.jsx` or a small new wrapper component): each
route's content fades+rises in on mount (keyed by `location.pathname` via
`useLocation`, triggering a CSS animation on the outlet's wrapper).
**Explicit scope limitation:** this is an *enter* transition only, not a
true exit/cross-fade — a real exit transition needs an animation
library (e.g. Framer Motion) to hold the outgoing page in the DOM during
the transition, which is more than this project's YAGNI-conscious,
zero-extra-dependency approach justifies. An enter-only fade is a real,
noticeable improvement over an instant hard-cut with no added
dependency.

## Technical approach

- No new npm dependencies. Everything above is achievable with plain
  CSS (`@keyframes`, custom properties, `::before`/`::after`,
  `clip-path`) plus one small custom hook (`useInView`, a thin
  IntersectionObserver wrapper, ~15 lines) and a few `mousemove`/`scroll`
  event handlers.
- New file: `frontend/src/hooks/useInView.js` — the shared
  IntersectionObserver hook, used by `PostCard` (entrance) and possibly
  the hero (if scroll-triggered replay is desired — out of scope, hero
  animates once on initial mount only).
- Keyframes/tokens live in `frontend/src/index.css` (global, alongside
  existing design-system rules) rather than a new file, to keep the
  single-source-of-truth pattern already established for CSS variables.

## Out of scope (this phase)

Images (Phase 2, not yet built — this phase's animations are designed to
still make sense once images exist, e.g. the card spotlight/hover glow
will work the same with or without an image, but no image-specific
animation like a zoom-on-hover is speced here since there's no image to
zoom yet). A JS animation library (Framer Motion, GSAP) — deliberately
avoided per YAGNI; everything here is achievable in plain CSS + minimal
JS. True route exit-transitions (see Page Transitions above). Sound
effects. Dark/light theme toggle (app is dark-only by design, unrelated
to this phase).

## Testing

Manual/browser verification, consistent with the rest of this project:
visually confirm each animation triggers correctly, confirm
`prefers-reduced-motion: reduce` (togglable via Chrome DevTools or OS
setting) actually suppresses/shortens the new animations, confirm no
layout shift or jank (animations should use `transform`/`opacity` where
possible, not properties that trigger layout, for smooth 60fps motion).
