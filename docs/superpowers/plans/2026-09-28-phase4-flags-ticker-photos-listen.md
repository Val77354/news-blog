# Phase 4: Flags, Ticker, Real Photos, Listen Bar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flag emoji on every country, a CNN-style scrolling breaking-news ticker above the navbar on every page, real photography on all 12 demo posts (via Lorem Picsum, not scraped/copyrighted images), and a functional "Listen" bar on Home that reads the latest post aloud using the browser's built-in text-to-speech.

**Architecture:** All additive to the existing design system — no new npm dependencies (emoji for flags, plain CSS marquee for the ticker, `window.speechSynthesis` for audio). A single `resolveImageUrl` helper unifies handling of the two `image_url` shapes now in play: relative `/uploads/...` paths (real uploads, Phase 2) and absolute `https://...` URLs (seeded demo photos, this phase).

**Tech Stack:** Same as the existing project — FastAPI/SQLAlchemy 2.0/SQLite backend, React/Vite frontend, plain CSS, `window.speechSynthesis` (no new dependency).

**Spec:** `docs/superpowers/specs/2026-09-28-phase4-flags-ticker-photos-listen-design.md`

## Global Constraints

- No new npm dependencies.
- Every new CSS rule is appended, not editing existing rules in place.
- `image_url` may now be either a relative `/uploads/...` path or an absolute `https://...` URL — every place that builds an image `src` from it must go through the shared `resolveImageUrl` helper, never hand-concatenate `API_URL` + `image_url` directly.
- The ticker and the listen-bar's equalizer animation must both be silenced/frozen under `prefers-reduced-motion: reduce` — the ticker specifically needs a scoped rule (the global override alone would freeze it mid-scroll, which reads as broken); the equalizer is already covered by the existing global override from Phase 3.
- No automated test suite — manual/browser verification, matching the rest of this project.
- All commits use `git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit ...` — this machine's global git config has a different fallback identity; verify with `git log -1 --format="%an <%ae>"` after every commit.
- Backend on port 8000, frontend dev server on port 5173 (unchanged).
- This session has repeatedly accumulated stale backend dev-server processes on port 8000, at least one of which was found silently serving old code despite a healthy-looking response. Before trusting any already-running backend, verify it's current via `curl -s http://localhost:8000/openapi.json` and check the routes you expect are present — don't trust a bare `GET /` 200.
- Every file this plan modifies was read in full immediately before this plan was written — the "current" content quoted or described in each task is verified accurate, not reconstructed from memory.

---

### Task 1: Country flags

**Files:**
- Modify: `frontend/src/constants.js`
- Modify: `frontend/src/components/CountryFilter.jsx`
- Modify: `frontend/src/components/PostCard.jsx`
- Modify: `frontend/src/pages/PostDetail.jsx`

**Interfaces:** Produces `COUNTRY_FLAGS` (object, country name → flag emoji) exported from `frontend/src/constants.js` — every consumer in this task imports it by this exact name.

- [ ] **Step 1: Append `COUNTRY_FLAGS` to `frontend/src/constants.js`**

Add to the end of the file:

```js

export const COUNTRY_FLAGS = {
  'United Kingdom': '🇬🇧',
  France: '🇫🇷',
  Germany: '🇩🇪',
  Italy: '🇮🇹',
  Spain: '🇪🇸',
  Netherlands: '🇳🇱',
  Poland: '🇵🇱',
  Sweden: '🇸🇪',
  Ukraine: '🇺🇦',
  Greece: '🇬🇷',
  Portugal: '🇵🇹',
  Switzerland: '🇨🇭',
}
```

- [ ] **Step 2: Add flags to `frontend/src/components/CountryFilter.jsx`**

Find:
```jsx
import { COUNTRIES } from '../constants'
```
Replace with:
```jsx
import { COUNTRIES, COUNTRY_FLAGS } from '../constants'
```

Find:
```jsx
            <span className="country-filter-box" aria-hidden="true">
              <svg viewBox="0 0 16 16" className="country-filter-check">
                <polyline points="3,8 7,12 13,4" />
              </svg>
            </span>
            {country}
```
Replace with:
```jsx
            <span className="country-filter-box" aria-hidden="true">
              <svg viewBox="0 0 16 16" className="country-filter-check">
                <polyline points="3,8 7,12 13,4" />
              </svg>
            </span>
            {COUNTRY_FLAGS[country]} {country}
```

- [ ] **Step 3: Add a flag to the country badge in `frontend/src/components/PostCard.jsx`**

Find:
```jsx
import { useInView } from '../hooks/useInView'
import { API_URL } from '../api/posts'
```
Replace with:
```jsx
import { useInView } from '../hooks/useInView'
import { API_URL } from '../api/posts'
import { COUNTRY_FLAGS } from '../constants'
```

Find:
```jsx
        <span className="country-badge">{post.country}</span>
```
Replace with:
```jsx
        <span className="country-badge">
          {COUNTRY_FLAGS[post.country]} {post.country}
        </span>
```

- [ ] **Step 4: Add a flag to the country badge in `frontend/src/pages/PostDetail.jsx`**

Find:
```jsx
import { API_URL, getPost, deletePost } from '../api/posts'
```
Replace with:
```jsx
import { API_URL, getPost, deletePost } from '../api/posts'
import { COUNTRY_FLAGS } from '../constants'
```

Find:
```jsx
        <span className="country-badge">{post.country}</span>
```
Replace with:
```jsx
        <span className="country-badge">
          {COUNTRY_FLAGS[post.country]} {post.country}
        </span>
```

- [ ] **Step 5: Verify live in the browser**

Start both servers. On the Home page, confirm every country in the country-filter checklist now shows a flag emoji before its name. Confirm every post card's country badge shows a flag + name. Open a post's detail page, confirm the same there.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/constants.js frontend/src/components/CountryFilter.jsx frontend/src/components/PostCard.jsx frontend/src/pages/PostDetail.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add flag emoji to country filter and badges"
```

---

### Task 2: Shared `resolveImageUrl` helper

**Files:**
- Modify: `frontend/src/api/posts.js`
- Modify: `frontend/src/components/PostCard.jsx`
- Modify: `frontend/src/pages/PostDetail.jsx`
- Modify: `frontend/src/components/PostForm.jsx`

**Interfaces:** Produces `resolveImageUrl(imageUrl)` from `frontend/src/api/posts.js` — returns `null` for a falsy input, the URL as-is if it already starts with `http`, otherwise `API_URL` prepended. Every image `src` in the app goes through this from here on.

This task exists because seeded demo posts (Task 3, next) will carry absolute `https://picsum.photos/...` URLs, while real uploads (Phase 2) carry relative `/uploads/...` paths — both must resolve to a correct, directly-usable `src`.

- [ ] **Step 1: Add `resolveImageUrl` to `frontend/src/api/posts.js`**

Find:
```js
export const API_URL = 'http://localhost:8000'
```
Replace with:
```js
export const API_URL = 'http://localhost:8000'

export function resolveImageUrl(imageUrl) {
  if (!imageUrl) return null
  return imageUrl.startsWith('http') ? imageUrl : `${API_URL}${imageUrl}`
}
```

- [ ] **Step 2: Use it in `frontend/src/components/PostCard.jsx`**

Find:
```jsx
import { API_URL } from '../api/posts'
```
Replace with:
```jsx
import { resolveImageUrl } from '../api/posts'
```

Find:
```jsx
          src={`${API_URL}${post.image_url}`}
```
Replace with:
```jsx
          src={resolveImageUrl(post.image_url)}
```

- [ ] **Step 3: Use it in `frontend/src/pages/PostDetail.jsx`**

Find:
```jsx
import { API_URL, getPost, deletePost } from '../api/posts'
```
Replace with:
```jsx
import { resolveImageUrl, getPost, deletePost } from '../api/posts'
```

Find:
```jsx
          src={`${API_URL}${post.image_url}`}
```
Replace with:
```jsx
          src={resolveImageUrl(post.image_url)}
```

- [ ] **Step 4: Use it in `frontend/src/components/PostForm.jsx`**

Find:
```jsx
import { API_URL } from '../api/posts'
```
Replace with:
```jsx
import { resolveImageUrl } from '../api/posts'
```

Find:
```jsx
  const [previewUrl, setPreviewUrl] = useState(
    initialValues.image_url ? `${API_URL}${initialValues.image_url}` : null,
  )
```
Replace with:
```jsx
  const [previewUrl, setPreviewUrl] = useState(resolveImageUrl(initialValues.image_url))
```

- [ ] **Step 5: Verify live in the browser**

Start both servers. Open the Home page — the 12 seeded posts don't have images yet (that's Task 3, next), so nothing should look different yet; confirm no console errors. Create a post with a real uploaded image (via `/posts/new`) — confirm it still displays correctly on the card and detail page (proving the relative-path branch of `resolveImageUrl` still works). Edit that post — confirm the existing image still previews correctly in the form. Delete the test post afterward via `DELETE /posts/{id}`.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/posts.js frontend/src/components/PostCard.jsx frontend/src/pages/PostDetail.jsx frontend/src/components/PostForm.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add resolveImageUrl helper to support absolute and relative image URLs"
```

---

### Task 3: Real photos on the 12 seeded posts

**Files:**
- Modify: `backend/seed.py`

**Interfaces:** Every entry in `SAMPLE_POSTS` gains an `image_url` key pointing at a stable `https://picsum.photos/seed/<slug>/800/450` URL.

- [ ] **Step 1: Replace `backend/seed.py` in full**

```python
from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

SAMPLE_POSTS = [
    {
        "title": "London Fintech Startups Report Record Funding Quarter",
        "content": (
            "London's fintech sector posted its strongest quarter in three "
            "years, with early-stage startups pulling in significantly more "
            "venture capital than the same period last year, according to "
            "industry trackers.\n\n"
            "Founders point to renewed investor confidence following a "
            "stretch of high interest rates, though some warn the rebound "
            "remains concentrated in a handful of well-connected firms."
        ),
        "author": "Emma Whitfield",
        "category": "Technology",
        "country": "United Kingdom",
        "image_url": "https://picsum.photos/seed/newsblog-1/800/450",
    },
    {
        "title": "Paris Hosts Emergency Summit on Mediterranean Migration Routes",
        "content": (
            "Leaders from a dozen countries met in Paris this week to "
            "discuss a coordinated response to a sharp rise in crossings "
            "along Mediterranean migration routes.\n\n"
            "The summit produced a joint statement on expanded "
            "search-and-rescue funding but stopped short of agreeing on a "
            "shared resettlement quota, a sticking point in similar talks "
            "for years."
        ),
        "author": "Marc Dubois",
        "category": "World",
        "country": "France",
        "image_url": "https://picsum.photos/seed/newsblog-2/800/450",
    },
    {
        "title": "German Manufacturers Warn of Energy Cost Squeeze Heading Into Winter",
        "content": (
            "Industry groups representing German manufacturers cautioned "
            "that rising energy costs could force some smaller producers "
            "to cut shifts or relocate production abroad.\n\n"
            "The warning comes as the government weighs new subsidies "
            "aimed at keeping energy-intensive industries competitive "
            "against producers in lower-cost regions."
        ),
        "author": "Klara Hoffmann",
        "category": "Business",
        "country": "Germany",
        "image_url": "https://picsum.photos/seed/newsblog-3/800/450",
    },
    {
        "title": "Italian Researchers Track Volcanic Activity With New Seismic Network",
        "content": (
            "A newly deployed network of seismic sensors around southern "
            "Italy's volcanic region is giving researchers their most "
            "detailed picture yet of underground magma movement.\n\n"
            "Scientists say the denser sensor coverage could extend "
            "eruption warning times from hours to potentially days in some "
            "scenarios."
        ),
        "author": "Giulia Romano",
        "category": "Science",
        "country": "Italy",
        "image_url": "https://picsum.photos/seed/newsblog-4/800/450",
    },
    {
        "title": "Spanish League Clubs Push Back Against Expanded Tournament Calendar",
        "content": (
            "Several top-flight Spanish clubs have formally objected to "
            "proposals that would add more mid-week fixtures to an already "
            "crowded football calendar.\n\n"
            "Player welfare groups have echoed the concern, citing rising "
            "injury rates linked to insufficient recovery time between "
            "matches."
        ),
        "author": "Javier Moreno",
        "category": "Sports",
        "country": "Spain",
        "image_url": "https://picsum.photos/seed/newsblog-5/800/450",
    },
    {
        "title": "Dutch Ports Expand Capacity Amid Shifting European Trade Routes",
        "content": (
            "Rotterdam and other major Dutch ports are investing heavily "
            "in new capacity as shipping routes adjust to ongoing "
            "disruptions elsewhere in Europe.\n\n"
            "Port authorities say the expansion is intended to secure the "
            "Netherlands' position as a primary gateway for goods entering "
            "the continent."
        ),
        "author": "Sanne de Vries",
        "category": "World",
        "country": "Netherlands",
        "image_url": "https://picsum.photos/seed/newsblog-6/800/450",
    },
    {
        "title": "Polish Manufacturing Rebounds as Nearshoring Trend Accelerates",
        "content": (
            "Poland's manufacturing sector posted its fastest growth in "
            "over a year, driven partly by Western European companies "
            "relocating supply chains closer to home.\n\n"
            "Economists say the nearshoring trend has been a consistent "
            "tailwind for the country's industrial base since global "
            "shipping costs began climbing."
        ),
        "author": "Tomasz Kowalski",
        "category": "Business",
        "country": "Poland",
        "image_url": "https://picsum.photos/seed/newsblog-7/800/450",
    },
    {
        "title": "Swedish Battery Startup Secures Funding for Gigafactory Expansion",
        "content": (
            "A Swedish battery manufacturer announced new funding to "
            "expand production capacity, positioning itself as a key "
            "supplier for the region's growing electric vehicle industry.\n\n"
            "The company said the expansion would roughly double its "
            "annual output once completed, though it declined to give a "
            "firm timeline."
        ),
        "author": "Elin Berg",
        "category": "Technology",
        "country": "Sweden",
        "image_url": "https://picsum.photos/seed/newsblog-8/800/450",
    },
    {
        "title": "Reconstruction Efforts Continue in Eastern Regions Amid Funding Gaps",
        "content": (
            "Local officials in several eastern towns say reconstruction "
            "of housing and infrastructure remains slow, with available "
            "funding falling well short of estimated needs.\n\n"
            "International donors have pledged continued support, though "
            "disbursement timelines remain a source of frustration for "
            "regional administrators."
        ),
        "author": "Olena Petrenko",
        "category": "World",
        "country": "Ukraine",
        "image_url": "https://picsum.photos/seed/newsblog-9/800/450",
    },
    {
        "title": "Greek Marine Biologists Document Rare Coral Recovery in Aegean Sea",
        "content": (
            "A survey team monitoring reef health in the Aegean Sea "
            "reported unexpected signs of coral recovery in areas "
            "previously damaged by warming waters.\n\n"
            "Researchers caution the recovery is localized and likely "
            "dependent on specific current patterns that keep water "
            "temperatures lower than surrounding areas."
        ),
        "author": "Dimitra Alexiou",
        "category": "Science",
        "country": "Greece",
        "image_url": "https://picsum.photos/seed/newsblog-10/800/450",
    },
    {
        "title": "Portuguese Youth Academies Draw International Scouting Interest",
        "content": (
            "A wave of international scouts has been visiting Portuguese "
            "youth academies this season, drawn by a string of standout "
            "performances in regional tournaments.\n\n"
            "Club officials say the increased attention has already led "
            "to several transfer inquiries for players as young as "
            "sixteen."
        ),
        "author": "Rui Fernandes",
        "category": "Sports",
        "country": "Portugal",
        "image_url": "https://picsum.photos/seed/newsblog-11/800/450",
    },
    {
        "title": "Swiss Banks Tighten Lending Standards Amid Regional Uncertainty",
        "content": (
            "Several major Swiss banks have quietly tightened lending "
            "standards for commercial borrowers, citing caution around "
            "broader economic uncertainty in the region.\n\n"
            "Small business groups say the shift has made it harder for "
            "growing companies to secure the credit lines they'd relied "
            "on in previous years."
        ),
        "author": "Lukas Meier",
        "category": "Business",
        "country": "Switzerland",
        "image_url": "https://picsum.photos/seed/newsblog-12/800/450",
    },
]


def seed():
    db = SessionLocal()
    try:
        if db.query(models.Post).count() > 0:
            print("Posts already exist, skipping seed.")
            return
        for data in SAMPLE_POSTS:
            db.add(models.Post(**data))
        db.commit()
        print(f"Seeded {len(SAMPLE_POSTS)} posts.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
```

- [ ] **Step 2: Delete the stale dev database and reseed**

```bash
cd backend
source venv/Scripts/activate
rm -f news_blog.db
python seed.py
```

Expected output: `Seeded 12 posts.`

- [ ] **Step 3: Verify**

```bash
uvicorn app.main:app --reload --port 8000
```

In another terminal: `curl -s http://localhost:8000/posts | grep -o '"image_url":"[^"]*"'` — expect 12 lines, each a `https://picsum.photos/seed/newsblog-N/800/450` URL. Open `https://picsum.photos/seed/newsblog-1/800/450` directly in a browser to confirm the service actually serves a real image (not an error page). Stop the server.

- [ ] **Step 4: Commit**

```bash
cd ..
git add backend/seed.py
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Seed demo posts with real Lorem Picsum photography"
```

---

### Task 4: Breaking-news ticker

**Files:**
- Create: `frontend/src/components/Ticker.jsx`
- Create: `frontend/src/components/Ticker.css`
- Modify: `frontend/src/App.jsx`

**Interfaces:** Consumes `listPosts()` from `frontend/src/api/posts.js`. `Ticker` takes no props — self-contained, fetches its own data.

Current `frontend/src/App.jsx` (verified):
```jsx
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import PostDetail from './pages/PostDetail'
import NewPost from './pages/NewPost'
import EditPost from './pages/EditPost'

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/posts/new" element={<NewPost />} />
        <Route path="/posts/:id" element={<PostDetail />} />
        <Route path="/posts/:id/edit" element={<EditPost />} />
      </Routes>
    </>
  )
}
```

- [ ] **Step 1: Create `frontend/src/components/Ticker.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listPosts } from '../api/posts'
import './Ticker.css'

export default function Ticker() {
  const [posts, setPosts] = useState([])

  useEffect(() => {
    listPosts()
      .then((data) => setPosts(data.slice(0, 5)))
      .catch(() => setPosts([]))
  }, [])

  if (posts.length === 0) return null

  return (
    <div className="ticker">
      <span className="ticker-label">Breaking</span>
      <div className="ticker-track">
        <div className="ticker-content">
          {posts.map((post) => (
            <Link key={post.id} to={`/posts/${post.id}`} className="ticker-item">
              {post.title}
            </Link>
          ))}
        </div>
        <div className="ticker-content" aria-hidden="true">
          {posts.map((post) => (
            <Link key={post.id} to={`/posts/${post.id}`} className="ticker-item">
              {post.title}
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
```

(The content is rendered twice back-to-back so the CSS animation can translate by exactly `-50%` and loop seamlessly — the second copy is `aria-hidden` since it's a visual duplicate, not new content.)

- [ ] **Step 2: Create `frontend/src/components/Ticker.css`**

```css
.ticker {
  display: flex;
  align-items: center;
  background: var(--accent);
  color: #12100e;
  overflow: hidden;
  white-space: nowrap;
}

.ticker-label {
  flex-shrink: 0;
  font-weight: 700;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 8px 16px;
  background: #12100e;
  color: var(--accent);
}

.ticker-track {
  display: flex;
  animation: ticker-scroll 30s linear infinite;
}

.ticker-content {
  display: flex;
  flex-shrink: 0;
}

.ticker-item {
  color: #12100e;
  font-weight: 600;
  font-size: 0.9rem;
  padding: 8px 32px;
  text-decoration: none;
  border-right: 1px solid rgba(18, 16, 14, 0.25);
}

.ticker-item:hover {
  text-decoration: underline;
}

@keyframes ticker-scroll {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(-50%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .ticker-track {
    animation: none;
  }
  .ticker-content[aria-hidden='true'] {
    display: none;
  }
}
```

(The global `prefers-reduced-motion` override from Phase 3 only zeroes `animation-duration`, which would leave the ticker frozen mid-scroll — this scoped rule instead sets `animation-name` to `none` via the shorthand, cleanly stopping it, and hides the duplicate copy so only one static headline row shows.)

- [ ] **Step 3: Mount the ticker in `frontend/src/App.jsx`**

Replace the file in full:

```jsx
import { Routes, Route } from 'react-router-dom'
import Ticker from './components/Ticker'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import PostDetail from './pages/PostDetail'
import NewPost from './pages/NewPost'
import EditPost from './pages/EditPost'

export default function App() {
  return (
    <>
      <Ticker />
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/posts/new" element={<NewPost />} />
        <Route path="/posts/:id" element={<PostDetail />} />
        <Route path="/posts/:id/edit" element={<EditPost />} />
      </Routes>
    </>
  )
}
```

- [ ] **Step 4: Verify live in the browser**

Start both servers. Confirm the ticker appears above the navbar on the Home page with a "BREAKING" label and 5 scrolling headlines. Watch it for several seconds — confirm the scroll loops seamlessly (no visible jump/reset). Click a headline — confirm it navigates to that post's detail page, and confirm the ticker is still visible there (mounted globally, not just on Home). In Chrome DevTools, emulate `prefers-reduced-motion: reduce` (Command Palette → "Show Rendering" → the media feature toggle) and reload — confirm the ticker shows one static row of headlines with no scrolling, not a frozen mid-scroll frame. Turn emulation back off afterward.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/Ticker.jsx frontend/src/components/Ticker.css frontend/src/App.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add breaking-news ticker above the navbar"
```

---

### Task 5: `useSpeech` hook

**Files:**
- Create: `frontend/src/hooks/useSpeech.js`

**Interfaces:** Produces `useSpeech(text)` — returns `{ speaking, toggle }`. `speaking` is a boolean; `toggle()` starts speaking `text` aloud if not already speaking, or stops immediately if it is.

- [ ] **Step 1: Create `frontend/src/hooks/useSpeech.js`**

```js
import { useEffect, useRef, useState } from 'react'

export function useSpeech(text) {
  const [speaking, setSpeaking] = useState(false)
  const utteranceRef = useRef(null)

  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel()
    }
  }, [])

  function play() {
    if (!text) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
    setSpeaking(true)
  }

  function stop() {
    window.speechSynthesis.cancel()
    setSpeaking(false)
  }

  function toggle() {
    if (speaking) {
      stop()
    } else {
      play()
    }
  }

  return { speaking, toggle }
}
```

(This deliberately uses cancel-and-restart rather than the Web Speech API's native `pause()`/`resume()` — those are known to be unreliable across browsers, especially Chrome, where a paused utterance can silently lose its position. A clean stop/start is simpler and more predictable at this scope.)

- [ ] **Step 2: Verify**

This hook has no visible UI on its own — it's wired into `ListenBar` in Task 6. Confirm there are no syntax errors:

```bash
cd frontend
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/hooks/useSpeech.js
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add useSpeech hook for text-to-speech playback"
```

---

### Task 6: "Listen" bar on Home

**Files:**
- Create: `frontend/src/components/ListenBar.jsx`
- Create: `frontend/src/components/ListenBar.css`
- Modify: `frontend/src/pages/Home.jsx`

**Interfaces:** Consumes `listPosts()` (`frontend/src/api/posts.js`) and `useSpeech` (Task 5). `ListenBar` takes no props.

Current `frontend/src/pages/Home.jsx` (verified — only the two find/replace blocks below change; everything else in the file stays the same):
```jsx
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { listPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import CategoryTabs from '../components/CategoryTabs'
import CountryFilter from '../components/CountryFilter'
import './Home.css'
```
...
```jsx
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>

      <CategoryTabs active={activeCategory} onChange={setActiveCategory} />
```

- [ ] **Step 1: Create `frontend/src/components/ListenBar.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listPosts } from '../api/posts'
import { useSpeech } from '../hooks/useSpeech'
import './ListenBar.css'

export default function ListenBar() {
  const [latest, setLatest] = useState(null)

  useEffect(() => {
    listPosts()
      .then((data) => setLatest(data[0] || null))
      .catch(() => setLatest(null))
  }, [])

  const text = latest ? `${latest.title}. ${latest.content}` : ''
  const { speaking, toggle } = useSpeech(text)

  if (!latest) return null

  return (
    <div className="listen-bar">
      <button
        type="button"
        className={`listen-play${speaking ? ' listen-play-active' : ''}`}
        onClick={toggle}
        aria-label={speaking ? 'Stop listening' : 'Listen to this story'}
      >
        {speaking ? (
          <span className="listen-equalizer" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
        ) : (
          <svg viewBox="0 0 16 16" className="listen-play-icon">
            <polygon points="4,3 13,8 4,13" />
          </svg>
        )}
      </button>
      <div className="listen-copy">
        <span className="listen-label">Listen</span>
        <Link to={`/posts/${latest.id}`} className="listen-title">
          {latest.title}
        </Link>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create `frontend/src/components/ListenBar.css`**

```css
.listen-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-4);
}

.listen-play {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: var(--accent);
  color: #12100e;
  cursor: pointer;
  transition: transform var(--dur-fast) var(--ease-out);
}

.listen-play:hover {
  transform: scale(1.08);
}

.listen-play-icon {
  width: 16px;
  height: 16px;
  fill: #12100e;
}

.listen-equalizer {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 16px;
}

.listen-equalizer span {
  width: 3px;
  background: #12100e;
  border-radius: 1px;
  animation: listen-bounce 0.8s ease-in-out infinite;
}

.listen-equalizer span:nth-child(1) {
  animation-delay: 0ms;
}

.listen-equalizer span:nth-child(2) {
  animation-delay: 150ms;
}

.listen-equalizer span:nth-child(3) {
  animation-delay: 300ms;
}

@keyframes listen-bounce {
  0%,
  100% {
    height: 4px;
  }
  50% {
    height: 16px;
  }
}

.listen-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.listen-label {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
}

.listen-title {
  color: var(--text);
  font-weight: 600;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

(The `listen-bounce` keyframe animation is already covered by the existing global `prefers-reduced-motion` override from Phase 3 — no extra scoped rule needed here, unlike the ticker.)

- [ ] **Step 3: Wire `ListenBar` into `frontend/src/pages/Home.jsx`**

Find:
```jsx
import { listPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import CategoryTabs from '../components/CategoryTabs'
import CountryFilter from '../components/CountryFilter'
import './Home.css'
```
Replace with:
```jsx
import { listPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import CategoryTabs from '../components/CategoryTabs'
import CountryFilter from '../components/CountryFilter'
import ListenBar from '../components/ListenBar'
import './Home.css'
```

Find:
```jsx
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>

      <CategoryTabs active={activeCategory} onChange={setActiveCategory} />
```
Replace with:
```jsx
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>

      <ListenBar />

      <CategoryTabs active={activeCategory} onChange={setActiveCategory} />
```

- [ ] **Step 4: Verify live in the browser**

Start both servers. On the Home page, confirm a "Listen" bar appears below the hero, above the category tabs, showing the latest post's title and a play button. Click play — confirm the browser actually speaks the post's title and content aloud, and the button switches to an animated equalizer icon while speaking. Click it again (now showing the equalizer) — confirm speech stops immediately and the button reverts to the play icon. Click the title text itself — confirm it navigates to that post's detail page.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ListenBar.jsx frontend/src/components/ListenBar.css frontend/src/pages/Home.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add Listen bar with text-to-speech playback to Home"
```

---

### Task 7: Final verification and push

**Files:** none — this is a verification-and-push-only task.

**Interfaces:** none.

- [ ] **Step 1: Full end-to-end walkthrough**

Start both servers (verify the backend is current per the Global Constraints note). Walk through, in order:
1. Confirm flags render everywhere countries appear (filter list, card badges, detail badges).
2. Confirm the ticker scrolls above the navbar on every page (Home, a post detail, New Post) and a headline click navigates correctly.
3. Confirm all 12 seeded posts show real photography on both the card grid and their detail pages.
4. Confirm the Listen bar speaks the latest post aloud and its play/stop toggle works.
5. Confirm nothing from prior phases regressed: category/country filtering, creating/editing/deleting a post (with and without an image), the save-toast, the animated hover effects on buttons/cards/tabs.

- [ ] **Step 2: Commit and push**

If Step 1 required no code changes (expected — this task is verification only), push whatever is currently unpushed from Tasks 1-6:

```bash
git push origin main
```

- [ ] **Step 3: Verify the push**

```bash
git log --oneline -1 origin/main
git status
```

Confirm `origin/main` matches local `HEAD` and the working tree is clean.

---
