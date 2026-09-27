# Phase 1: Country + Category Filters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `country` field to posts, a category tab bar, and a multi-select country filter, so the Home feed can be narrowed by category and/or country — starting with 12 European countries.

**Architecture:** `country` is a plain string column on `Post`, exactly like the existing `category` column — no enum, no separate table. `GET /posts` gains optional `category`/`countries` query params, filtered server-side. The frontend gets a single shared `constants.js` (CATEGORIES, COUNTRIES) consumed by both the new filter UI and the post form's dropdowns.

**Tech Stack:** Same as the existing project — FastAPI/SQLAlchemy 2.0/SQLite backend, React/Vite frontend, plain CSS.

**Spec:** `docs/superpowers/specs/2026-09-27-phase1-country-category-filters-design.md`

## Global Constraints

- `country` is a plain string column (like `category`), no enum, no separate table.
- `GET /posts` filtering is server-side via optional `category` and `countries` (comma-separated) query params, combined with AND logic.
- `frontend/src/constants.js` (`CATEGORIES`, `COUNTRIES`) is the single source of truth for both the filter UI and `PostForm`'s dropdowns — never duplicate these lists.
- `category` becomes a `<select>` dropdown in `PostForm` (replacing the current free-text input), for filtering reliability.
- No automated test suite — manual/browser verification, matching the rest of this project.
- All commits use `git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit ...`.
- The dev SQLite database (`backend/news_blog.db`) is gitignored/disposable — safe to delete and reseed when the schema changes.
- Backend on port 8000, frontend dev server on port 5173 (unchanged).

---

### Task 1: Backend — country column, schema field, reseed

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/seed.py`

**Interfaces:**
- Produces: `Post.country: str` column, `PostBase.country: str` field (flows into `PostCreate`/`PostUpdate`/`PostOut`) — every later task that touches a `Post`'s shape depends on this field existing.

- [ ] **Step 1: Add `country` to `backend/app/models.py`**

Add this line to the `Post` class, directly after the existing `category` column:

```python
    country: Mapped[str] = mapped_column(String(100))
```

- [ ] **Step 2: Add `country` to `backend/app/schemas.py`**

Add `country: str` to `PostBase`, directly after `category: str`, so the class reads:

```python
class PostBase(BaseModel):
    title: str
    content: str
    author: str
    category: str
    country: str
```

- [ ] **Step 3: Replace `SAMPLE_POSTS` in `backend/seed.py`**

Replace the existing `SAMPLE_POSTS` list (keep everything else in the file — the `seed()` function, imports, `if __name__ == "__main__"` block — unchanged) with this 12-post list, one post per country:

```python
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
    },
]
```

- [ ] **Step 4: Delete the stale dev database and reseed**

The existing `backend/news_blog.db` has the old schema (no `country` column) and may hold posts created during manual testing — SQLAlchemy's `create_all` does not alter existing tables, so the file must be deleted, not just re-run against.

```bash
cd backend
source venv/Scripts/activate
rm -f news_blog.db
python seed.py
```

Expected output: `Seeded 12 posts.`

- [ ] **Step 5: Verify**

```bash
uvicorn app.main:app --reload --port 8000
```

In another terminal: `curl -s http://localhost:8000/posts | grep -o '"country":"[^"]*"' ` — expect 12 lines, one per country in the list above (order may vary). Stop the server.

- [ ] **Step 6: Commit**

```bash
cd ..
git add backend/app/models.py backend/app/schemas.py backend/seed.py
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add country field to Post model, schema, and seed data"
```

---

### Task 2: Backend — category/country query-param filtering

**Files:**
- Modify: `backend/app/routers/posts.py`

**Interfaces:**
- Consumes: `models.Post.country`, `models.Post.category` from Task 1.
- Produces: `GET /posts` accepts optional `category: str` and `countries: str` (comma-separated) query params — later frontend tasks call this exact shape.

- [ ] **Step 1: Update `list_posts` in `backend/app/routers/posts.py`**

Replace the existing `list_posts` function with:

```python
@router.get("", response_model=list[schemas.PostOut])
def list_posts(
    category: str | None = None,
    countries: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Post)
    if category:
        query = query.filter(models.Post.category == category)
    if countries:
        country_list = [c.strip() for c in countries.split(",") if c.strip()]
        if country_list:
            query = query.filter(models.Post.country.in_(country_list))
    return query.order_by(models.Post.created_at.desc()).all()
```

(Leave every other function in the file — `get_post`, `create_post`, `update_post`, `delete_post` — untouched.)

- [ ] **Step 2: Verify**

```bash
cd backend
source venv/Scripts/activate
uvicorn app.main:app --reload --port 8000
```

In another terminal, run each and check the result:

```bash
curl -s "http://localhost:8000/posts?category=Technology" | grep -o '"category":"[^"]*"'
# expect only "Technology" entries (2 of them)

curl -s "http://localhost:8000/posts?countries=France,Germany" | grep -o '"country":"[^"]*"'
# expect only "France" and "Germany" entries (1 each)

curl -s "http://localhost:8000/posts?category=World&countries=France,Ukraine" | grep -o '"country":"[^"]*"'
# expect only France and Ukraine (both are World-category posts)

curl -s "http://localhost:8000/posts" | grep -c '"id"'
# expect 12 (no filters = everything)
```

Stop the server.

- [ ] **Step 3: Commit**

```bash
cd ..
git add backend/app/routers/posts.py
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add category/countries query-param filtering to GET /posts"
```

---

### Task 3: Frontend — shared constants + API client params

**Files:**
- Create: `frontend/src/constants.js`
- Modify: `frontend/src/api/posts.js`

**Interfaces:**
- Produces: `frontend/src/constants.js` exports `CATEGORIES` (array of 5 strings) and `COUNTRIES` (array of 12 strings) — every later frontend task in this plan imports from here, never redeclares the lists.
- Produces: `listPosts({ category, countries } = {})` — `category` is an optional string, `countries` is an optional array of strings. Existing callers using `listPosts()` with no arguments continue to work unchanged.

- [ ] **Step 1: Create `frontend/src/constants.js`**

```js
export const CATEGORIES = ['Technology', 'Business', 'World', 'Science', 'Sports']

export const COUNTRIES = [
  'United Kingdom',
  'France',
  'Germany',
  'Italy',
  'Spain',
  'Netherlands',
  'Poland',
  'Sweden',
  'Ukraine',
  'Greece',
  'Portugal',
  'Switzerland',
]
```

- [ ] **Step 2: Update `listPosts` in `frontend/src/api/posts.js`**

Replace the existing `listPosts` function with:

```js
export function listPosts({ category, countries } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (countries && countries.length > 0) params.set('countries', countries.join(','))
  const qs = params.toString()
  return fetch(`${API_URL}/posts${qs ? `?${qs}` : ''}`).then(handleResponse)
}
```

(Leave `getPost`, `createPost`, `updatePost`, `deletePost`, and `handleResponse` untouched.)

- [ ] **Step 3: Verify**

Start the backend (`cd backend && source venv/Scripts/activate && uvicorn app.main:app --reload --port 8000`) and frontend (`cd frontend && npm run dev`). The Home page still calls `listPosts()` with no arguments (not updated until Task 4) — confirm it still loads all 12 posts with no errors, proving the new optional-params signature is backward compatible. Stop both servers.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/constants.js frontend/src/api/posts.js
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add shared category/country constants and API client filter params"
```

---

### Task 4: Frontend — CategoryTabs, CountryFilter, Home wiring

**Files:**
- Create: `frontend/src/components/CategoryTabs.jsx`
- Create: `frontend/src/components/CategoryTabs.css`
- Create: `frontend/src/components/CountryFilter.jsx`
- Create: `frontend/src/components/CountryFilter.css`
- Modify: `frontend/src/pages/Home.jsx`

**Interfaces:**
- Consumes: `CATEGORIES`, `COUNTRIES` from `frontend/src/constants.js` (Task 3); `listPosts({ category, countries })` from `frontend/src/api/posts.js` (Task 3).
- Produces: `CategoryTabs` props `{ active, onChange }` — `active` is `null` (meaning "All") or a category string; `onChange(value)` is called with the newly selected value (`null` for "All"). `CountryFilter` props `{ selected, onChange }` — `selected` is an array of currently-checked country strings; `onChange(newArray)` is called with the full updated array on every checkbox toggle.

- [ ] **Step 1: Create `frontend/src/components/CategoryTabs.css`**

```css
.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-bottom: var(--space-3);
  border-bottom: 1px solid var(--border);
  padding-bottom: var(--space-2);
}

.category-tab {
  font-family: var(--font-body);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-dim);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 8px 16px;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}

.category-tab:hover {
  color: var(--text);
  background: var(--bg-elevated);
}

.category-tab.active {
  color: var(--accent);
  background: var(--accent-dim);
  border-color: var(--accent);
}
```

- [ ] **Step 2: Create `frontend/src/components/CategoryTabs.jsx`**

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

- [ ] **Step 3: Create `frontend/src/components/CountryFilter.css`**

```css
.country-filter {
  margin-bottom: var(--space-4);
}

.country-filter-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: var(--space-1);
}

.country-filter-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.country-filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: var(--text-dim);
  cursor: pointer;
}

/* index.css applies width/padding/border/background to every <input> for
   the post-form's text fields — reset those properties specifically for
   this checkbox so it renders as a normal checkbox, not a filled box. */
.country-filter-item input[type='checkbox'] {
  all: revert;
  accent-color: var(--accent);
  cursor: pointer;
}
```

- [ ] **Step 4: Create `frontend/src/components/CountryFilter.jsx`**

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

- [ ] **Step 5: Replace `frontend/src/pages/Home.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { listPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import CategoryTabs from '../components/CategoryTabs'
import CountryFilter from '../components/CountryFilter'
import './Home.css'

export default function Home() {
  const [posts, setPosts] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [activeCategory, setActiveCategory] = useState(null)
  const [selectedCountries, setSelectedCountries] = useState([])

  useEffect(() => {
    setStatus('loading')
    listPosts({ category: activeCategory, countries: selectedCountries })
      .then((data) => {
        setPosts(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [activeCategory, selectedCountries])

  return (
    <div className="page container">
      <header className="hero">
        <h1>Stories worth your morning coffee.</h1>
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>

      <CategoryTabs active={activeCategory} onChange={setActiveCategory} />
      <CountryFilter selected={selectedCountries} onChange={setSelectedCountries} />

      {status === 'loading' && <p className="state-message">Loading posts…</p>}
      {status === 'error' && <p className="state-message error">Couldn't load posts: {error}</p>}
      {status === 'ready' && posts.length === 0 && (
        <p className="state-message">No posts match these filters.</p>
      )}

      {status === 'ready' && posts.length > 0 && (
        <div className="post-grid">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 6: Verify live in the browser**

Start both servers. Open `http://localhost:5173/`. Confirm: category tabs render (All + 5 categories) with "All" active by default and all 12 posts showing; clicking "Technology" narrows the grid to 2 posts; clicking "All" restores 12. Check the "France" and "Germany" country checkboxes — confirm the grid narrows to those 2 countries' posts (combined with whichever category tab is active). Uncheck both — confirm it goes back to showing all countries for the active category. Use Chrome automation tools if available.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/CategoryTabs.jsx frontend/src/components/CategoryTabs.css frontend/src/components/CountryFilter.jsx frontend/src/components/CountryFilter.css frontend/src/pages/Home.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add CategoryTabs and CountryFilter, wire filtering into Home"
```

---

### Task 5: Frontend — country badges, form dropdowns, final verification

**Files:**
- Modify: `frontend/src/index.css`
- Modify: `frontend/src/components/PostCard.jsx`
- Modify: `frontend/src/pages/PostDetail.jsx`
- Modify: `frontend/src/components/PostForm.jsx`
- Modify: `frontend/src/components/PostForm.css`
- Modify: `frontend/src/pages/EditPost.jsx`

**Interfaces:**
- Consumes: `CATEGORIES`, `COUNTRIES` from `frontend/src/constants.js` (Task 3).
- Produces: `.badge-row` and `.country-badge` global CSS classes (alongside the existing `.category-pill`), used by both `PostCard` and `PostDetail`.

- [ ] **Step 1: Update `frontend/src/index.css`**

Find the existing `.category-pill` rule and remove its `margin-bottom: var(--space-2);` line (spacing moves to the new wrapping `.badge-row` instead — leave every other property unchanged):

```css
.category-pill {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--accent);
  background: var(--accent-dim);
  padding: 3px 10px;
  border-radius: 999px;
}
```

Immediately after that rule, add:

```css
.country-badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-dim);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  padding: 3px 10px;
  border-radius: 999px;
}

.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
  margin-bottom: var(--space-2);
}
```

Find the existing `input, textarea { ... }` rule's selector line and add `select` to it, so `<select>` dropdowns get the same styling as text inputs:

```css
input,
textarea,
select {
```

(The rest of that rule's body — everything inside the `{ }` — stays exactly as it is; only the selector list gains `select`.)

- [ ] **Step 2: Update `frontend/src/components/PostCard.jsx`**

Replace the single `<span className="category-pill">{post.category}</span>` line with:

```jsx
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
```

(Everything else in the file stays the same.)

- [ ] **Step 3: Update `frontend/src/pages/PostDetail.jsx`**

Replace the single `<span className="category-pill">{post.category}</span>` line (in the `'ready'` branch's return) with:

```jsx
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
```

(Everything else in the file stays the same.)

- [ ] **Step 4: Update `frontend/src/components/PostForm.css`**

Find the `.post-form-row` rule and its `label` child rule; replace both with:

```css
.post-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.post-form-row label {
  flex: 1 1 160px;
}
```

(`flex-wrap: wrap` and a `160px` basis let the three fields — Author/Category/Country — wrap onto multiple lines on narrow screens instead of squeezing.)

- [ ] **Step 5: Replace `frontend/src/components/PostForm.jsx`**

```jsx
import { useState } from 'react'
import { CATEGORIES, COUNTRIES } from '../constants'
import './PostForm.css'

const EMPTY = { title: '', content: '', author: '', category: '', country: '' }

export default function PostForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Publish' }) {
  const [values, setValues] = useState(initialValues)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  function update(field) {
    return (e) => setValues((v) => ({ ...v, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await onSubmit(values)
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  return (
    <form className="post-form" onSubmit={handleSubmit}>
      <label>
        Title
        <input value={values.title} onChange={update('title')} required />
      </label>
      <div className="post-form-row">
        <label>
          Author
          <input value={values.author} onChange={update('author')} required />
        </label>
        <label>
          Category
          <select value={values.category} onChange={update('category')} required>
            <option value="" disabled>
              Select a category
            </option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label>
          Country
          <select value={values.country} onChange={update('country')} required>
            <option value="" disabled>
              Select a country
            </option>
            {COUNTRIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        Content
        <textarea value={values.content} onChange={update('content')} required />
      </label>
      <div className="post-form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </button>
        {error && <span className="state-message error">{error}</span>}
      </div>
    </form>
  )
}
```

- [ ] **Step 6: Update `frontend/src/pages/EditPost.jsx`**

Add `country: post.country,` to the `initialValues` object passed to `PostForm`, so it reads:

```jsx
      <PostForm
        initialValues={{
          title: post.title,
          content: post.content,
          author: post.author,
          category: post.category,
          country: post.country,
        }}
        onSubmit={handleSubmit}
        submitLabel="Save Changes"
      />
```

(Everything else in the file stays the same.)

- [ ] **Step 7: Verify live in the browser — full walkthrough**

Start both servers. On the Home page, confirm every post card now shows two badges (category pill + country badge). Click into a post's detail page, confirm the same two badges appear there. Click "New Post": confirm Category and Country are now dropdowns (not free-text), populated with the 5 categories / 12 countries; fill in all fields including selecting a category and country, submit, confirm the new post's detail page shows the correct badges. Edit an existing post: confirm the Category/Country dropdowns are pre-filled with that post's current values, change the country, save, confirm the updated country badge shows on the detail page and in the home grid. Use Chrome automation tools if available.

- [ ] **Step 8: Commit and push**

```bash
git add frontend/src/index.css frontend/src/components/PostCard.jsx frontend/src/pages/PostDetail.jsx frontend/src/components/PostForm.jsx frontend/src/components/PostForm.css frontend/src/pages/EditPost.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add country badges to post views, category/country dropdowns to PostForm"
git push origin main
```

- [ ] **Step 9: Verify the push**

```bash
git log --oneline -1 origin/main
git status
```

Confirm `origin/main` matches local `HEAD` and the working tree is clean.

---
