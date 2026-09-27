# Phase 3: Animated Design System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing dark editorial design "heavy" with a real, cohesive motion system — animated buttons, sliding tab indicator, staggered/spotlight post cards, custom animated checkboxes, skeleton loading, a save-success toast, an animated hero, a shrinking navbar, and page-enter transitions — all in plain CSS plus minimal JS, no new dependencies.

**Architecture:** A shared token/keyframe library lives in `frontend/src/index.css` (durations, easings, `@keyframes`), consumed by every component's own CSS. One small shared hook (`frontend/src/hooks/useInView.js`) drives scroll-triggered entrance animations. Every new CSS rule in this plan is *appended* to the end of its file rather than edited in place — the existing rules and their current values are left untouched, so there's no risk of a stale assumption about a file's current exact content silently breaking something. A final reduced-motion pass makes the whole system respect `prefers-reduced-motion`.

**Tech Stack:** Same as the existing project — React 19/Vite/React Router v7 frontend, plain CSS. No new npm dependencies.

**Spec:** `docs/superpowers/specs/2026-09-28-phase3-animated-design-design.md`

## Global Constraints

- No new npm dependencies — everything is plain CSS (`@keyframes`, custom properties, `::before`/`::after`) plus minimal vanilla JS (one IntersectionObserver hook, a couple of event listeners).
- Every new CSS rule is **appended** to the end of the relevant file, never edited in place — this preserves every existing rule exactly as it is today.
- All new animation timing must reference the shared tokens (`--ease-out`, `--ease-spring`, `--dur-fast`, `--dur-base`, `--dur-slow`) added in Task 1, not hardcoded values.
- `@media (prefers-reduced-motion: reduce)` must suppress/shorten every animation added in this phase (final task).
- No automated test suite — manual/browser verification, matching the rest of this project.
- All commits use `git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit ...`.
- Backend on port 8000, frontend dev server on port 5173 (unchanged).
- Every file this plan modifies was read in full immediately before this plan was written — the "current" content quoted or described in each task is verified accurate, not reconstructed from memory.

---

### Task 1: Foundation — tokens, keyframes, reduced-motion-safe utility class, useInView hook

**Files:**
- Modify: `frontend/src/index.css` (append only)
- Create: `frontend/src/hooks/useInView.js`

**Interfaces:**
- Produces: CSS custom properties `--ease-out`, `--ease-spring`, `--dur-fast`, `--dur-base`, `--dur-slow`; `@keyframes` named `fade-up`, `shimmer`, `shake`, `pulse-scale`, `drift`, `sweep`; utility class `.fade-up-item` — every later task in this plan references these by exact name.
- Produces: `useInView(options)` — a hook returning `[ref, inView]`. `ref` must be attached to the DOM node to observe; `inView` becomes `true` (and stays `true`) once the node enters the viewport. Default `options` is `{ threshold: 0.15 }`.

- [ ] **Step 1: Append new tokens and keyframes to `frontend/src/index.css`**

Add this entire block to the very end of the file:

```css

/* ---- Phase 3: animation tokens & keyframe library ---- */

:root {
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --dur-fast: 150ms;
  --dur-base: 300ms;
  --dur-slow: 600ms;
}

@keyframes fade-up {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shimmer {
  from {
    background-position: -200% 0;
  }
  to {
    background-position: 200% 0;
  }
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  20% {
    transform: translateX(-4px);
  }
  40% {
    transform: translateX(4px);
  }
  60% {
    transform: translateX(-3px);
  }
  80% {
    transform: translateX(3px);
  }
}

@keyframes pulse-scale {
  0% {
    transform: scale(0.6);
    opacity: 0;
  }
  60% {
    transform: scale(1.1);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes drift {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(30px, -20px);
  }
}

@keyframes sweep {
  from {
    transform: translateX(-150%) skewX(-15deg);
  }
  to {
    transform: translateX(250%) skewX(-15deg);
  }
}

.fade-up-item {
  opacity: 0;
  animation: fade-up var(--dur-slow) var(--ease-out) forwards;
}
```

(A second `:root { ... }` block is valid CSS — it merges with the first, adding these five new custom properties without touching the original block.)

- [ ] **Step 2: Create `frontend/src/hooks/useInView.js`**

```js
import { useEffect, useRef, useState } from 'react'

export function useInView(options = { threshold: 0.15 }) {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setInView(true)
        observer.disconnect()
      }
    }, options)

    observer.observe(node)
    return () => observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return [ref, inView]
}
```

- [ ] **Step 3: Verify**

This task has no visible UI on its own (the hook isn't wired into any component until Task 4, and the keyframes aren't used by any element until later tasks). Confirm there are no syntax errors instead:

```bash
cd frontend
npm run build
```

Expected: build succeeds with no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/index.css frontend/src/hooks/useInView.js
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add Phase 3 animation tokens, keyframes, and useInView hook"
```

---

### Task 2: Animated buttons — bracket reveal, shine sweep, shake

**Files:**
- Modify: `frontend/src/index.css` (append only)

**Interfaces:**
- Consumes: `--accent`, `--accent-dim`, `--radius` (existing tokens), `--ease-out`, `--dur-base`, `--dur-slow` and the `sweep`/`shake` keyframes (Task 1).

The current `.btn`/`.btn-primary`/`.btn-danger`/`.btn-ghost` rules (already in `index.css`, lines 73-120) are left completely untouched — every rule below is a **new** rule block using the same selectors (or `::before`/`::after` on them), which CSS simply merges with the existing declarations.

- [ ] **Step 1: Append button animations to `frontend/src/index.css`**

```css

/* ---- Phase 3: button animations ---- */

.btn {
  position: relative;
}

.btn:not(.btn-primary):not(.btn-danger)::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: calc(var(--radius) + 4px);
  opacity: 0;
  background: linear-gradient(var(--accent), var(--accent)) top left / 10px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) top left / 2px 10px no-repeat,
    linear-gradient(var(--accent), var(--accent)) top right / 10px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) top right / 2px 10px no-repeat,
    linear-gradient(var(--accent), var(--accent)) bottom left / 10px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) bottom left / 2px 10px no-repeat,
    linear-gradient(var(--accent), var(--accent)) bottom right / 10px 2px no-repeat,
    linear-gradient(var(--accent), var(--accent)) bottom right / 2px 10px no-repeat;
  transition: opacity var(--dur-base) var(--ease-out), inset var(--dur-base) var(--ease-out);
  pointer-events: none;
}

.btn:not(.btn-primary):not(.btn-danger):hover::before {
  opacity: 1;
  inset: -6px;
}

.btn-primary {
  position: relative;
  overflow: hidden;
}

.btn-primary::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 40%;
  height: 100%;
  background: linear-gradient(115deg, transparent, rgba(255, 255, 255, 0.45), transparent);
  transform: translateX(-150%) skewX(-15deg);
  pointer-events: none;
}

.btn-primary:hover::after {
  animation: sweep var(--dur-slow) var(--ease-out);
}

.btn-danger:hover {
  animation: shake var(--dur-slow) var(--ease-out);
}
```

This gives: plain/ghost buttons (`.btn` without `.btn-primary`/`.btn-danger`) four small corner brackets that fade in and expand outward on hover; the primary button a diagonal light sweep across it on hover; the danger button a brief shake on hover.

- [ ] **Step 2: Verify live in the browser**

Start the frontend (`cd frontend && npm run dev`; backend not required for this visual check, but start it too if you want real data: `cd backend && source venv/Scripts/activate && uvicorn app.main:app --reload --port 8000`). Open `http://localhost:5173/`. Hover the navbar's "New Post" button (`.btn-primary`) — confirm a light diagonal sweep plays once across it. Navigate to any post's detail page, hover "Edit" (`.btn`, plain) — confirm four small corner brackets fade in and expand slightly outward from the button's edges. Hover "Delete" (`.btn-danger`) — confirm it shakes briefly. Use Chrome automation tools if available.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/index.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add animated corner-bracket, shine-sweep, and shake button hovers"
```

---

### Task 3: Sliding category tab indicator

**Files:**
- Modify: `frontend/src/components/CategoryTabs.jsx` (full replacement)
- Modify: `frontend/src/components/CategoryTabs.css` (append only)

**Interfaces:**
- Props unchanged: `{ active, onChange }` (`active` is `null` for "All" or a category string).

The current `CategoryTabs.jsx` (verified below) is being fully replaced to add ref-based measurement for the sliding indicator; `CategoryTabs.css`'s existing rules are untouched, only appended to.

Current `CategoryTabs.jsx` (for reference — this is exactly what's being replaced):
```jsx
import { CATEGORIES } from '../constants'
import './CategoryTabs.css'

export default function CategoryTabs({ active, onChange }) {
  const tabs = ['All', ...CATEGORIES]

  return (
    <div className="category-tabs">
      {tabs.map((tab) => {
        const isActive = tab === 'All' ? active === null : active === tab
        return (
          <button
            key={tab}
            type="button"
            className={`category-tab${isActive ? ' active' : ''}`}
            onClick={() => onChange(tab === 'All' ? null : tab)}
          >
            {tab}
          </button>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 1: Replace `frontend/src/components/CategoryTabs.jsx`**

```jsx
import { useEffect, useRef, useState } from 'react'
import { CATEGORIES } from '../constants'
import './CategoryTabs.css'

export default function CategoryTabs({ active, onChange }) {
  const tabs = ['All', ...CATEGORIES]
  const containerRef = useRef(null)
  const tabRefs = useRef({})
  const [indicatorStyle, setIndicatorStyle] = useState({ width: 0, left: 0 })

  useEffect(() => {
    const activeKey = active === null ? 'All' : active
    const node = tabRefs.current[activeKey]
    const container = containerRef.current
    if (node && container) {
      const nodeRect = node.getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      setIndicatorStyle({
        width: nodeRect.width,
        left: nodeRect.left - containerRect.left,
      })
    }
  }, [active])

  return (
    <div className="category-tabs" ref={containerRef}>
      <span className="category-tab-indicator" style={indicatorStyle} />
      {tabs.map((tab) => {
        const isActive = tab === 'All' ? active === null : active === tab
        return (
          <button
            key={tab}
            type="button"
            ref={(el) => {
              tabRefs.current[tab] = el
            }}
            className={`category-tab${isActive ? ' active' : ''}`}
            onClick={() => onChange(tab === 'All' ? null : tab)}
          >
            {tab}
          </button>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 2: Append to `frontend/src/components/CategoryTabs.css`**

```css

/* ---- Phase 3: sliding indicator ---- */

.category-tabs {
  position: relative;
}

.category-tab-indicator {
  position: absolute;
  top: 0;
  bottom: var(--space-2);
  border-radius: 999px;
  background: var(--accent-dim);
  border: 1px solid var(--accent);
  transition: left var(--dur-base) var(--ease-spring), width var(--dur-base) var(--ease-spring);
  z-index: 0;
  pointer-events: none;
}

.category-tab {
  position: relative;
  z-index: 1;
}
```

**Note:** the indicator's `top`/`bottom` values are a reasonable starting guess for aligning it behind the tab row (the container has `padding-bottom` and a `border-bottom` below the tabs that the indicator shouldn't cover). If it looks visually misaligned against the real rendered tabs in the browser — floating above/below them, or a noticeably wrong height — adjust `top`/`bottom` until it lines up. Getting it pixel-perfect isn't critical; looking clearly "behind the active tab and sliding smoothly" is what matters.

- [ ] **Step 3: Verify live in the browser**

Start both servers, open the Home page. Confirm a soft accent-colored pill sits behind the "All" tab by default. Click "Technology" — confirm the pill smoothly slides and resizes to sit behind "Technology" instead of instantly jumping. Click through a couple more tabs to confirm the slide animation is smooth and the pill's width matches each tab's text width reasonably closely.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/CategoryTabs.jsx frontend/src/components/CategoryTabs.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add sliding indicator animation to CategoryTabs"
```

---

### Task 4: Post card entrance stagger, hover glow, cursor spotlight

**Files:**
- Modify: `frontend/src/components/PostCard.jsx` (full replacement)
- Modify: `frontend/src/components/PostCard.css` (append only)
- Modify: `frontend/src/pages/Home.jsx` (one-line change)

**Interfaces:**
- Consumes: `useInView` from `frontend/src/hooks/useInView.js` (Task 1).
- `PostCard` gains a new optional prop `index` (defaults to `0`), used to stagger each card's entrance delay.

Current `PostCard.jsx` (verified — being fully replaced):
```jsx
import { Link } from 'react-router-dom'
import './PostCard.css'

function excerpt(content, length = 140) {
  const flat = content.replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}…` : flat
}

export default function PostCard({ post }) {
  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  return (
    <Link to={`/posts/${post.id}`} className="post-card">
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h2>{post.title}</h2>
      <p className="post-card-excerpt">{excerpt(post.content)}</p>
      <div className="post-card-meta">
        {post.author} · {date}
      </div>
    </Link>
  )
}
```

- [ ] **Step 1: Replace `frontend/src/components/PostCard.jsx`**

```jsx
import { Link } from 'react-router-dom'
import { useInView } from '../hooks/useInView'
import './PostCard.css'

function excerpt(content, length = 140) {
  const flat = content.replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}…` : flat
}

export default function PostCard({ post, index = 0 }) {
  const [ref, inView] = useInView()
  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect()
    e.currentTarget.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
    e.currentTarget.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
  }

  return (
    <Link
      to={`/posts/${post.id}`}
      className={`post-card${inView ? ' fade-up-item' : ''}`}
      style={inView ? { animationDelay: `${Math.min(index, 8) * 60}ms` } : { opacity: 0 }}
      ref={ref}
      onMouseMove={handleMouseMove}
    >
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h2>{post.title}</h2>
      <p className="post-card-excerpt">{excerpt(post.content)}</p>
      <div className="post-card-meta">
        {post.author} · {date}
      </div>
    </Link>
  )
}
```

- [ ] **Step 2: Append to `frontend/src/components/PostCard.css`**

```css

/* ---- Phase 3: hover glow + cursor spotlight ---- */

.post-card {
  position: relative;
  overflow: hidden;
}

.post-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(
    220px circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
    var(--accent-dim),
    transparent 70%
  );
  opacity: 0;
  transition: opacity var(--dur-base) var(--ease-out);
  pointer-events: none;
}

.post-card:hover::before {
  opacity: 1;
}

.post-card:hover {
  box-shadow: 0 0 0 1px var(--accent), 0 12px 24px -8px var(--accent-dim);
}
```

- [ ] **Step 3: Pass `index` to `PostCard` in `frontend/src/pages/Home.jsx`**

Find:
```jsx
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
```
Replace with:
```jsx
          {posts.map((post, index) => (
            <PostCard key={post.id} post={post} index={index} />
          ))}
```

- [ ] **Step 4: Verify live in the browser**

Start both servers, open the Home page. Confirm the post cards fade+rise into view with a slight stagger (each card starting a little after the previous one) rather than all appearing instantly at once. Move the mouse across a card without clicking — confirm a soft glowing highlight follows the cursor within the card. Hover a card — confirm it lifts slightly and gets a glowing accent-colored outline/shadow. Scroll down if there are enough cards to have some below the fold, and confirm cards that were off-screen also animate in as they scroll into view (not just the initial batch).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/PostCard.jsx frontend/src/components/PostCard.css frontend/src/pages/Home.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add staggered entrance, hover glow, and cursor spotlight to PostCard"
```

---

### Task 5: Custom animated country checkboxes

**Files:**
- Modify: `frontend/src/components/CountryFilter.jsx` (full replacement)
- Modify: `frontend/src/components/CountryFilter.css` (append only)

**Interfaces:** Props unchanged: `{ selected, onChange }`.

Current `CountryFilter.jsx` (verified — being fully replaced):
```jsx
import { COUNTRIES } from '../constants'
import './CountryFilter.css'

export default function CountryFilter({ selected, onChange }) {
  function toggle(country) {
    if (selected.includes(country)) {
      onChange(selected.filter((c) => c !== country))
    } else {
      onChange([...selected, country])
    }
  }

  return (
    <div className="country-filter">
      <span className="country-filter-label">Countries</span>
      <div className="country-filter-list">
        {COUNTRIES.map((country) => (
          <label key={country} className="country-filter-item">
            <input
              type="checkbox"
              checked={selected.includes(country)}
              onChange={() => toggle(country)}
            />
            {country}
          </label>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 1: Replace `frontend/src/components/CountryFilter.jsx`**

```jsx
import { COUNTRIES } from '../constants'
import './CountryFilter.css'

export default function CountryFilter({ selected, onChange }) {
  function toggle(country) {
    if (selected.includes(country)) {
      onChange(selected.filter((c) => c !== country))
    } else {
      onChange([...selected, country])
    }
  }

  return (
    <div className="country-filter">
      <span className="country-filter-label">Countries</span>
      <div className="country-filter-list">
        {COUNTRIES.map((country) => (
          <label key={country} className="country-filter-item">
            <input
              type="checkbox"
              className="country-filter-checkbox"
              checked={selected.includes(country)}
              onChange={() => toggle(country)}
            />
            <span className="country-filter-box" aria-hidden="true">
              <svg viewBox="0 0 16 16" className="country-filter-check">
                <polyline points="3,8 7,12 13,4" />
              </svg>
            </span>
            {country}
          </label>
        ))}
      </div>
    </div>
  )
}
```

(The real `<input type="checkbox">` stays in the DOM — still focusable, clickable, and readable by screen readers — it's just made visually invisible in CSS below, with a custom-styled sibling `<span>` standing in for it visually.)

- [ ] **Step 2: Append to `frontend/src/components/CountryFilter.css`**

```css

/* ---- Phase 3: custom animated checkbox ---- */

.country-filter-item {
  position: relative;
}

.country-filter-checkbox {
  position: absolute;
  opacity: 0;
  width: 18px;
  height: 18px;
  margin: 0;
  cursor: pointer;
}

.country-filter-box {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-elevated);
  transition: border-color var(--dur-fast) var(--ease-out), background var(--dur-fast) var(--ease-out);
  flex-shrink: 0;
}

.country-filter-check {
  width: 12px;
  height: 12px;
  fill: none;
  stroke: #12100e;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 20;
  stroke-dashoffset: 20;
  transition: stroke-dashoffset var(--dur-base) var(--ease-out);
}

.country-filter-checkbox:checked + .country-filter-box {
  background: var(--accent);
  border-color: var(--accent);
}

.country-filter-checkbox:checked + .country-filter-box .country-filter-check {
  stroke-dashoffset: 0;
}

.country-filter-checkbox:focus-visible + .country-filter-box {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

- [ ] **Step 3: Verify live in the browser**

Start both servers, open the Home page. Confirm the country filter now shows custom square checkboxes (rounded corners, matching the dark theme) instead of the browser's native checkbox style. Click one — confirm it fills with the accent color and a checkmark animates/draws itself in (not just appearing instantly). Uncheck it — confirm it reverts. Tab to a checkbox with the keyboard (Tab key) — confirm a visible focus outline appears. Confirm the filtering itself still works correctly (checking countries still narrows the post grid as before).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/CountryFilter.jsx frontend/src/components/CountryFilter.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add custom animated checkbox to CountryFilter"
```

---

### Task 6: Skeleton loading state

**Files:**
- Modify: `frontend/src/pages/Home.jsx` (one block change)
- Modify: `frontend/src/pages/Home.css` (append only)

**Interfaces:** none beyond what's already established.

- [ ] **Step 1: Replace the loading state in `frontend/src/pages/Home.jsx`**

Find:
```jsx
      {status === 'loading' && <p className="state-message">Loading posts…</p>}
```
Replace with:
```jsx
      {status === 'loading' && (
        <div className="post-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      )}
```

- [ ] **Step 2: Append to `frontend/src/pages/Home.css`**

```css

/* ---- Phase 3: skeleton loading ---- */

.skeleton-card {
  height: 220px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: linear-gradient(100deg, var(--bg-elevated) 30%, #232327 50%, var(--bg-elevated) 70%);
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}
```

- [ ] **Step 3: Verify**

Start both servers. Since the local backend responds almost instantly, the loading state may only be visible for a fraction of a second under normal use — that's expected and fine. To actually see it: open Chrome DevTools' Network tab, set throttling to "Slow 3G" (or similar), then reload the Home page or change a filter — confirm 6 shimmering skeleton card placeholders appear in the grid layout while the request is in flight, replaced by the real cards once it resolves. Turn throttling back off afterward.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Home.jsx frontend/src/pages/Home.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add shimmering skeleton cards for the loading state"
```

---

### Task 7: Save-success toast

**Files:**
- Modify: `frontend/src/pages/PostDetail.jsx` (full replacement)
- Modify: `frontend/src/pages/PostDetail.css` (append only)
- Modify: `frontend/src/pages/NewPost.jsx` (one-line change)
- Modify: `frontend/src/pages/EditPost.jsx` (one-line change)

**Interfaces:** none beyond what's already established.

**Note on this task vs. the design spec:** the spec's original idea was a checkmark pulse on the submit button *before* navigating away. In practice this doesn't work reliably: `PostForm`'s `onSubmit` prop (owned by `NewPost`/`EditPost`) both makes the API call *and* calls `navigate()` internally — by the time `PostForm` could react to "submission succeeded," the route change has already been triggered, so any success UI in `PostForm` itself would need to race the unmount and might never actually paint. This task implements the same underlying idea — visible positive feedback on a successful save — the reliable way instead: `NewPost`/`EditPost` pass a flag through React Router's navigation state, and `PostDetail` shows a brief animated toast on arrival if that flag is set. This has no race condition since it all happens after the new page has already mounted.

Current `PostDetail.jsx` (verified — being fully replaced):
```jsx
import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { getPost, deletePost } from '../api/posts'
import './PostDetail.css'

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [post, setPost] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    setStatus('loading')
    getPost(id)
      .then((data) => {
        setPost(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  async function handleDelete() {
    if (!window.confirm('Delete this post? This cannot be undone.')) return
    try {
      await deletePost(id)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  if (status === 'loading') {
    return (
      <div className="page container">
        <p className="state-message">Loading post…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page container">
        <p className="state-message error">Couldn't load post: {error}</p>
      </div>
    )
  }

  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="page container post-detail">
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h1>{post.title}</h1>
      <div className="post-detail-meta state-message">
        {post.author} · {date}
      </div>
      <p className="post-detail-body">{post.content}</p>
      <div className="post-detail-actions">
        <Link to={`/posts/${post.id}/edit`} className="btn">
          Edit
        </Link>
        <button className="btn btn-danger" onClick={handleDelete}>
          Delete
        </button>
      </div>
      {error && <p className="state-message error">{error}</p>}
    </div>
  )
}
```

- [ ] **Step 1: Replace `frontend/src/pages/PostDetail.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom'
import { getPost, deletePost } from '../api/posts'
import './PostDetail.css'

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [post, setPost] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [showToast, setShowToast] = useState(Boolean(location.state?.justSaved))

  useEffect(() => {
    setStatus('loading')
    getPost(id)
      .then((data) => {
        setPost(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  useEffect(() => {
    if (!showToast) return
    const timer = setTimeout(() => setShowToast(false), 2500)
    return () => clearTimeout(timer)
  }, [showToast])

  async function handleDelete() {
    if (!window.confirm('Delete this post? This cannot be undone.')) return
    try {
      await deletePost(id)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  if (status === 'loading') {
    return (
      <div className="page container">
        <p className="state-message">Loading post…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page container">
        <p className="state-message error">Couldn't load post: {error}</p>
      </div>
    )
  }

  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="page container post-detail">
      {showToast && (
        <div className="save-toast">
          <svg viewBox="0 0 16 16" className="save-toast-check">
            <polyline points="3,8 7,12 13,4" />
          </svg>
          {location.state?.message || 'Saved!'}
        </div>
      )}
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h1>{post.title}</h1>
      <div className="post-detail-meta state-message">
        {post.author} · {date}
      </div>
      <p className="post-detail-body">{post.content}</p>
      <div className="post-detail-actions">
        <Link to={`/posts/${post.id}/edit`} className="btn">
          Edit
        </Link>
        <button className="btn btn-danger" onClick={handleDelete}>
          Delete
        </button>
      </div>
      {error && <p className="state-message error">{error}</p>}
    </div>
  )
}
```

- [ ] **Step 2: Append to `frontend/src/pages/PostDetail.css`**

```css

/* ---- Phase 3: save-success toast ---- */

.save-toast {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  background: var(--accent);
  color: #12100e;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 8px 16px;
  border-radius: 999px;
  margin-bottom: var(--space-3);
  animation: pulse-scale var(--dur-base) var(--ease-spring);
}

.save-toast-check {
  width: 14px;
  height: 14px;
  fill: none;
  stroke: #12100e;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}
```

- [ ] **Step 3: Update `frontend/src/pages/NewPost.jsx`**

Find:
```jsx
    navigate(`/posts/${post.id}`)
```
Replace with:
```jsx
    navigate(`/posts/${post.id}`, { state: { justSaved: true, message: 'Post published!' } })
```

- [ ] **Step 4: Update `frontend/src/pages/EditPost.jsx`**

Find:
```jsx
    navigate(`/posts/${id}`)
```
Replace with:
```jsx
    navigate(`/posts/${id}`, { state: { justSaved: true, message: 'Changes saved!' } })
```

- [ ] **Step 5: Verify live in the browser**

Start both servers. Create a new post via the "New Post" form — confirm that after being taken to the new post's detail page, a small animated pill/toast reading "Post published!" briefly appears near the top of the page (with a checkmark), then fades away on its own after ~2.5 seconds. Edit an existing post and save — confirm the same toast appears reading "Changes saved!" this time. Reload a post detail page directly (not via a save) — confirm no toast appears (it should only show right after a save).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/PostDetail.jsx frontend/src/pages/PostDetail.css frontend/src/pages/NewPost.jsx frontend/src/pages/EditPost.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add save-success toast after creating or editing a post"
```

---

### Task 8: Animated hero

**Files:**
- Modify: `frontend/src/pages/Home.jsx` (one block change)
- Modify: `frontend/src/pages/Home.css` (append only)

**Interfaces:** none beyond what's already established.

- [ ] **Step 1: Replace the hero section in `frontend/src/pages/Home.jsx`**

Find:
```jsx
      <header className="hero">
        <h1>Stories worth your morning coffee.</h1>
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>
```
Replace with:
```jsx
      <header className="hero">
        <div className="hero-backdrop" aria-hidden="true" />
        <h1 className="hero-title">
          {'Stories worth your morning coffee.'.split(' ').map((word, i) => (
            <span key={i} className="hero-word" style={{ animationDelay: `${i * 80}ms` }}>
              {word}&nbsp;
            </span>
          ))}
        </h1>
        <span className="hero-underline" />
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>
```

- [ ] **Step 2: Append to `frontend/src/pages/Home.css`**

```css

/* ---- Phase 3: animated hero ---- */

.hero {
  position: relative;
  overflow: hidden;
}

.hero-backdrop {
  position: absolute;
  top: -100px;
  right: -80px;
  width: 360px;
  height: 360px;
  background: radial-gradient(circle, var(--accent-dim), transparent 70%);
  border-radius: 50%;
  filter: blur(20px);
  animation: drift 12s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

.hero-title {
  position: relative;
  z-index: 1;
}

.hero-word {
  display: inline-block;
  opacity: 0;
  animation: fade-up var(--dur-slow) var(--ease-out) forwards;
}

.hero-underline {
  display: block;
  height: 3px;
  width: 0;
  background: var(--accent);
  border-radius: 2px;
  margin-bottom: var(--space-3);
  animation: underline-sweep var(--dur-slow) var(--ease-out) 500ms forwards;
}

@keyframes underline-sweep {
  to {
    width: 120px;
  }
}
```

- [ ] **Step 3: Verify live in the browser**

Start both servers, open the Home page (a hard reload — Ctrl+Shift+R — makes it easier to see the entrance animation each time). Confirm the headline "Stories worth your morning coffee." fades/rises in word by word rather than appearing all at once. Confirm a short accent-colored underline sweeps in below the headline shortly after the words finish animating. Confirm a soft, large, blurred glow shape is visible near the top-right of the hero area, slowly drifting back and forth (watch for a few seconds — the drift cycle is 12 seconds, so give it a moment).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/Home.jsx frontend/src/pages/Home.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add staggered word reveal, underline sweep, and drifting backdrop to hero"
```

---

### Task 9: Shrinking navbar on scroll

**Files:**
- Modify: `frontend/src/components/Navbar.jsx` (full replacement)
- Modify: `frontend/src/components/Navbar.css` (append only)

**Interfaces:** none beyond what's already established.

Current `Navbar.jsx` (verified — being fully replaced):
```jsx
import { Link } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          The Daily<span>Wire</span>
        </Link>
        <Link to="/posts/new" className="btn btn-primary">
          New Post
        </Link>
      </div>
    </nav>
  )
}
```

- [ ] **Step 1: Replace `frontend/src/components/Navbar.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 24)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <nav className={`navbar${scrolled ? ' navbar-scrolled' : ''}`}>
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          The Daily<span>Wire</span>
        </Link>
        <Link to="/posts/new" className="btn btn-primary">
          New Post
        </Link>
      </div>
    </nav>
  )
}
```

- [ ] **Step 2: Append to `frontend/src/components/Navbar.css`**

```css

/* ---- Phase 3: shrink on scroll ---- */

.navbar-inner {
  transition: padding var(--dur-base) var(--ease-out);
}

.navbar-brand {
  transition: font-size var(--dur-base) var(--ease-out);
}

.navbar-scrolled .navbar-inner {
  padding-top: 10px;
  padding-bottom: 10px;
}

.navbar-scrolled .navbar-brand {
  font-size: 1.2rem;
}
```

- [ ] **Step 3: Verify live in the browser**

Start both servers, open the Home page (needs enough posts/content to actually scroll — it should, with 12 seeded posts). Scroll down a bit — confirm the navbar visibly shrinks (less padding, smaller brand text) smoothly, not instantly. Scroll back to the top — confirm it smoothly grows back to its original size.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/Navbar.jsx frontend/src/components/Navbar.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Shrink navbar on scroll"
```

---

### Task 10: Page-enter transitions, reduced-motion pass, final verification, push

**Files:**
- Modify: `frontend/src/index.css` (append only)

**Interfaces:** none — this is the final integration task.

- [ ] **Step 1: Add a page-enter animation to `frontend/src/index.css`**

The existing `.page` class (already used as the root wrapper on every page — Home, PostDetail, NewPost, EditPost) gets one new rule appended:

```css

/* ---- Phase 3: page-enter transition ---- */

.page {
  animation: fade-up var(--dur-slow) var(--ease-out) forwards;
}
```

Because React Router unmounts and remounts a page's component when navigating between *different* routes (e.g. Home → New Post, or Post Detail → Edit), the `.page` element is a fresh DOM node each time, so this animation naturally replays on every such navigation. **Known scope limit:** navigating between two different posts' detail pages (`/posts/1` → `/posts/2`) does NOT replay it, since that's the same route matching the same mounted component instance (only the `:id` param changes) — React Router does not remount in that case. This is consistent with the design spec's own documented limitation that this phase implements enter-only transitions, not a full cross-fade system requiring an animation library.

- [ ] **Step 2: Append the reduced-motion override to `frontend/src/index.css`**

```css

/* ---- Phase 3: respect prefers-reduced-motion ---- */

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }

  .fade-up-item,
  .hero-word,
  .page {
    opacity: 1 !important;
    transform: none !important;
  }

  .post-card::before,
  .hero-backdrop {
    display: none !important;
  }
}
```

This universal `*` selector catches every animation/transition added across this entire plan (and anything pre-existing) without needing to enumerate each one by name — the standard, robust pattern for a global reduced-motion override. The few explicit rules after it handle elements whose *resting* state (before/without their animation) would otherwise be invisible (`opacity: 0`) or show an unwanted decorative layer.

- [ ] **Step 3: Verify reduced motion**

In Chrome DevTools: open the Command Palette (Ctrl+Shift+P), run "Show Rendering", find "Emulate CSS media feature prefers-reduced-motion" and set it to "reduce". Reload the Home page — confirm the hero words, page content, and post cards all appear immediately (no fade/stagger delay), the hero's drifting backdrop and the card cursor-spotlight are gone, and hovering buttons no longer shows the sweep/shake/bracket animations (though basic color/border hover states from the original design can still change instantly — only the added *animations* need to be suppressed). Turn the emulation back to "No emulation" afterward.

- [ ] **Step 4: Full end-to-end verification of every animation from this plan**

With both servers running and reduced-motion emulation OFF, walk through: hero word-stagger + underline sweep + drifting backdrop (Task 8) → hover the primary/ghost/danger buttons for their respective animations (Task 2) → click category tabs and confirm the sliding indicator (Task 3) → scroll to see cards fade in staggered, hover a card for the spotlight+glow (Task 4) → check/uncheck a country checkbox for the draw-in animation (Task 5) → throttle network and reload to see the skeleton loader (Task 6) → create or edit a post and confirm the save-success toast (Task 7) → scroll the page to see the navbar shrink (Task 9) → navigate between Home and New Post to confirm the page-enter fade (Task 10). Use Chrome automation tools if available for this full walkthrough.

- [ ] **Step 5: Commit and push**

```bash
git add frontend/src/index.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add page-enter transition and reduced-motion support"
git push origin main
```

- [ ] **Step 6: Verify the push**

```bash
git log --oneline -1 origin/main
git status
```

Confirm `origin/main` matches local `HEAD` and the working tree is clean.

---
