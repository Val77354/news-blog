# Phase 2: Image Upload Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a post optionally carry one uploaded image — stored on the backend's disk, served via FastAPI's `StaticFiles`, shown on post cards (with a hover zoom) and the detail page, with old files cleaned up on delete/replace.

**Architecture:** `Post.image_url` is a plain nullable string column. Upload is a separate, stateless endpoint (`POST /uploads/image`) decoupled from post create/update — the frontend uploads the file first, gets back a URL, then includes that URL in the normal JSON post payload. Backend post-delete/update cleans up the old file from disk.

**Tech Stack:** Same as the existing project — FastAPI/SQLAlchemy 2.0/SQLite backend, React/Vite frontend, plain CSS. One new backend dependency: `python-multipart` (required by FastAPI for parsing uploaded files).

**Spec:** `docs/superpowers/specs/2026-09-28-phase2-image-upload-design.md`

## Global Constraints

- `image_url` is a plain nullable string column — no separate images table, no foreign key.
- Allowed image types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`. Max size: 5MB. Both enforced server-side with a 422 response.
- Uploaded files are saved under UUID-generated filenames (never the client-supplied filename) to `backend/uploads/`, gitignored.
- Deleting or updating a post's image cleans up the old file from disk, best-effort (a missing file is not an error).
- A post with no image renders with no reserved image space and no placeholder — image markup is always conditional on `post.image_url` being set.
- No automated test suite — manual/browser verification, matching the rest of this project.
- All commits use `git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit ...` — this machine's global git config has a different fallback identity; every prior phase on this project has had at least one near-miss from dropping these flags, so verify with `git log -1 --format="%an <%ae>"` after every commit in this plan.
- Backend on port 8000, frontend dev server on port 5173 (unchanged).
- Every file this plan modifies was read in full immediately before this plan was written — the "current" content quoted or described in each task is verified accurate, not reconstructed from memory.

---

### Task 1: Backend — image_url column, uploads dir, upload endpoint

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/main.py`
- Create: `backend/app/routers/uploads.py`
- Modify: `backend/requirements.txt`

**Interfaces:**
- Produces: `Post.image_url: str | None`, `PostBase.image_url: str | None = None` (flows into `PostCreate`/`PostUpdate`/`PostOut`).
- Produces: `POST /uploads/image` (multipart, field name `file`) → `{"url": "/uploads/<uuid>.<ext>"}` on success, 422 on invalid type/size.
- Produces: `backend/uploads/` served at `http://localhost:8000/uploads/<filename>` via `StaticFiles`.

- [ ] **Step 1: Install `python-multipart`**

```bash
cd backend
source venv/Scripts/activate
pip install python-multipart
pip freeze > requirements.txt
```

(This regenerates the full `requirements.txt` with the new dependency pinned — expected to add `python-multipart==<version>` as a new line; every other line should stay as it is today.)

- [ ] **Step 2: Add `image_url` to `backend/app/models.py`**

Add this line to the `Post` class, directly after the existing `country` column:

```python
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
```

- [ ] **Step 3: Add `image_url` to `backend/app/schemas.py`**

Add `image_url: str | None = None` to `PostBase`, directly after `country: str`, so the class reads:

```python
class PostBase(BaseModel):
    title: str
    content: str
    author: str
    category: str
    country: str
    image_url: str | None = None
```

- [ ] **Step 4: Create `backend/app/routers/uploads.py`**

```python
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = Path("uploads")

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/image")
async def upload_image(file: UploadFile):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only JPEG, PNG, WEBP, or GIF images are allowed.",
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Image must be smaller than 5MB.",
        )

    extension = ALLOWED_CONTENT_TYPES[file.content_type]
    filename = f"{uuid.uuid4()}{extension}"
    (UPLOAD_DIR / filename).write_bytes(contents)

    return {"url": f"/uploads/{filename}"}
```

- [ ] **Step 5: Wire the uploads directory, static mount, and router into `backend/app/main.py`**

Replace the file in full:

```python
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .routers import posts, uploads

models.Base.metadata.create_all(bind=engine)

Path("uploads").mkdir(exist_ok=True)

app = FastAPI(title="News Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(uploads.router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def read_root():
    return {"status": "ok", "service": "news-blog-api"}
```

- [ ] **Step 6: Verify**

```bash
uvicorn app.main:app --reload --port 8000
```

In another terminal, from the repo root, upload a real small image file:

```bash
# create a tiny valid PNG for testing
python -c "import pathlib; pathlib.Path('backend/test.png').write_bytes(bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108020000009077053f0000000a4944415478da6360000002000155ea52890000000049454e44ae426082'))"

curl -s -X POST http://localhost:8000/uploads/image -F "file=@backend/test.png;type=image/png"
# expect: {"url":"/uploads/<some-uuid>.png"}

IMAGE_URL=$(curl -s -X POST http://localhost:8000/uploads/image -F "file=@backend/test.png;type=image/png" | python -c "import sys,json; print(json.load(sys.stdin)['url'])")
curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000$IMAGE_URL"
# expect: 200 (the uploaded file is actually servable at its URL)

curl -s -X POST http://localhost:8000/uploads/image -F "file=@backend/app/main.py;type=text/plain" -w " status:%{http_code}\n"
# expect: 422 (wrong content type rejected)

ls backend/uploads
# expect: the uploaded .png file(s) present

rm backend/test.png
```

Stop the server.

- [ ] **Step 7: Commit**

```bash
cd ..
git add backend/app/models.py backend/app/schemas.py backend/app/main.py backend/app/routers/uploads.py backend/requirements.txt
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add image_url field and image upload endpoint"
```

---

### Task 2: Backend — clean up image files on post delete/update

**Files:**
- Modify: `backend/app/routers/posts.py`
- Modify: `backend/.gitignore`

**Interfaces:**
- Consumes: `models.Post.image_url` (Task 1).
- Produces: `_delete_image_file(image_url)` helper (module-private, used by `update_post` and `delete_post`).

- [ ] **Step 1: Add the cleanup helper and wire it into `update_post`/`delete_post` in `backend/app/routers/posts.py`**

Add this import at the top of the file, alongside the existing ones:

```python
from pathlib import Path
```

Add this helper function after the imports, before `router = APIRouter(...)`:

```python
def _delete_image_file(image_url: str | None) -> None:
    if not image_url:
        return
    file_path = Path("uploads") / Path(image_url).name
    file_path.unlink(missing_ok=True)
```

In `update_post`, add the cleanup check right after the existing `if db_post is None: raise ...` block, before the `for field, value in post.model_dump().items():` loop:

```python
    if post.image_url != db_post.image_url:
        _delete_image_file(db_post.image_url)
```

In `delete_post`, add the cleanup call right after the existing `if db_post is None: raise ...` block, before `db.delete(db_post)`:

```python
    _delete_image_file(db_post.image_url)
```

(Every other function and line in the file stays exactly as it is.)

- [ ] **Step 2: Add `uploads/` to `backend/.gitignore`**

Add this line to the existing file (which currently has `venv/`, `__pycache__/`, `*.pyc`, `*.db`):

```
uploads/
```

- [ ] **Step 3: Verify**

```bash
cd backend
source venv/Scripts/activate
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
# create a post with an image, then verify deleting it removes the file
python -c "import pathlib; pathlib.Path('backend/test.png').write_bytes(bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108020000009077053f0000000a4944415478da6360000002000155ea52890000000049454e44ae426082'))"

IMAGE_URL=$(curl -s -X POST http://localhost:8000/uploads/image -F "file=@backend/test.png;type=image/png" | python -c "import sys,json; print(json.load(sys.stdin)['url'])")
echo "Uploaded: $IMAGE_URL"

POST_ID=$(curl -s -X POST http://localhost:8000/posts -H "Content-Type: application/json" -d "{\"title\":\"Img Test\",\"content\":\"Body\",\"author\":\"A\",\"category\":\"Technology\",\"country\":\"France\",\"image_url\":\"$IMAGE_URL\"}" | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Created post: $POST_ID"

ls "backend${IMAGE_URL}" 2>/dev/null && echo "file exists before delete"

curl -s -X DELETE "http://localhost:8000/posts/$POST_ID" -w "delete status: %{http_code}\n"

ls "backend${IMAGE_URL}" 2>/dev/null || echo "file correctly gone after delete"

rm -f backend/test.png
```

Expect: the file exists before delete, and is confirmed gone after. Stop the server.

- [ ] **Step 4: Commit**

```bash
cd ..
git add backend/app/routers/posts.py backend/.gitignore
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Clean up image files when a post is deleted or its image replaced"
```

---

### Task 3: Frontend — uploads API client + PostForm image field

**Files:**
- Modify: `frontend/src/api/posts.js` (export `API_URL`)
- Create: `frontend/src/api/uploads.js`
- Modify: `frontend/src/components/PostForm.jsx` (full replacement)
- Modify: `frontend/src/components/PostForm.css`
- Modify: `frontend/src/pages/EditPost.jsx` (one-line addition)

**Interfaces:**
- Produces: `API_URL` now exported from `frontend/src/api/posts.js` — used by `PostForm`, `PostCard` (Task 4), and `PostDetail` (Task 5) to build full image URLs.
- Produces: `uploadImage(file)` from `frontend/src/api/uploads.js` — returns `Promise<{ url: string }>`, throws with a readable message on failure.
- `PostForm`'s `values` object now includes `image_url: string | null`, and its `onSubmit` callback receives that field like every other — `NewPost`/`EditPost` don't need any change to their own `handleSubmit` since they already pass `values` straight through to `createPost`/`updatePost`.

Current `frontend/src/api/posts.js` (verified — only the first line changes):
```js
const API_URL = 'http://localhost:8000'
```

- [ ] **Step 1: Export `API_URL` from `frontend/src/api/posts.js`**

Find:
```js
const API_URL = 'http://localhost:8000'
```
Replace with:
```js
export const API_URL = 'http://localhost:8000'
```
(Nothing else in the file changes.)

- [ ] **Step 2: Create `frontend/src/api/uploads.js`**

```js
import { API_URL } from './posts'

export async function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_URL}/uploads/image`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      const d = data.detail
      detail = Array.isArray(d) ? d.map((e) => e.msg).join(', ') : d || detail
    } catch {
      // response had no JSON body
    }
    throw new Error(detail)
  }

  return res.json()
}
```

Current `frontend/src/components/PostForm.jsx` (verified — being fully replaced):
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

- [ ] **Step 3: Replace `frontend/src/components/PostForm.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { CATEGORIES, COUNTRIES } from '../constants'
import { API_URL } from '../api/posts'
import { uploadImage } from '../api/uploads'
import './PostForm.css'

const EMPTY = { title: '', content: '', author: '', category: '', country: '', image_url: null }

export default function PostForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Publish' }) {
  const [values, setValues] = useState(initialValues)
  const [imageFile, setImageFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(
    initialValues.image_url ? `${API_URL}${initialValues.image_url}` : null,
  )
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  function update(field) {
    return (e) => setValues((v) => ({ ...v, [field]: e.target.value }))
  }

  function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setImageFile(file)
    setPreviewUrl(URL.createObjectURL(file))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      let imageUrl = values.image_url ?? null
      if (imageFile) {
        const result = await uploadImage(imageFile)
        imageUrl = result.url
      }
      await onSubmit({ ...values, image_url: imageUrl })
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
      <div className="post-form-image-field">
        <span className="post-form-image-caption">Image (optional)</span>
        <div className="post-form-image-picker">
          {previewUrl && <img src={previewUrl} alt="" className="post-form-image-preview" />}
          <label className="post-form-file-button">
            {previewUrl ? 'Change image' : 'Choose image'}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              className="post-form-file-input"
              onChange={handleFileChange}
            />
          </label>
        </div>
      </div>
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

- [ ] **Step 4: Append to `frontend/src/components/PostForm.css`**

```css

/* ---- Phase 2: image field ---- */

.post-form-image-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.9rem;
  color: var(--text-dim);
}

.post-form-image-picker {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.post-form-image-preview {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--radius);
  border: 1px solid var(--border);
}

.post-form label.post-form-file-button {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-family: var(--font-body);
  font-size: 0.95rem;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  cursor: pointer;
  width: fit-content;
  transition: border-color 0.15s ease;
}

.post-form-file-button:hover {
  border-color: var(--text-dim);
}

.post-form-file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

(The `.post-form label.post-form-file-button` selector — two classes plus the element type — is deliberately more specific than the existing `.post-form label { display: flex; flex-direction: column; ... }` rule earlier in this same file, so the file-picker button gets its own `inline-flex` layout instead of inheriting the generic label's column layout.)

- [ ] **Step 5: Add `image_url` to `EditPost.jsx`'s `initialValues`**

Find:
```jsx
        initialValues={{
          title: post.title,
          content: post.content,
          author: post.author,
          category: post.category,
          country: post.country,
        }}
```
Replace with:
```jsx
        initialValues={{
          title: post.title,
          content: post.content,
          author: post.author,
          category: post.category,
          country: post.country,
          image_url: post.image_url,
        }}
```

- [ ] **Step 6: Verify live in the browser**

Start both servers (`cd backend && source venv/Scripts/activate && uvicorn app.main:app --reload --port 8000`; `cd frontend && npm run dev`). Open `http://localhost:5173/posts/new`. Confirm an "Image (optional)" field with a "Choose image" button appears below Content. Pick an image file — confirm a preview thumbnail appears and the button now reads "Change image". Fill in the rest of the form and submit — confirm it creates successfully (the post detail page will still show no image since Task 5 hasn't wired up display yet — that's expected, just confirm no errors and the post was created). Open the browser's Network tab if you want to confirm a `POST /uploads/image` request fired before the `POST /posts` request.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/api/posts.js frontend/src/api/uploads.js frontend/src/components/PostForm.jsx frontend/src/components/PostForm.css frontend/src/pages/EditPost.jsx
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Add image upload field to PostForm"
```

---

### Task 4: Frontend — display image on PostCard

**Files:**
- Modify: `frontend/src/components/PostCard.jsx` (full replacement)
- Modify: `frontend/src/components/PostCard.css`

**Interfaces:** Consumes `API_URL` from `frontend/src/api/posts.js` (Task 3).

Current `frontend/src/components/PostCard.jsx` (verified — being fully replaced):
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

- [ ] **Step 1: Replace `frontend/src/components/PostCard.jsx`**

```jsx
import { Link } from 'react-router-dom'
import { useInView } from '../hooks/useInView'
import { API_URL } from '../api/posts'
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
      {post.image_url && (
        <img src={`${API_URL}${post.image_url}`} alt="" className="post-card-image" />
      )}
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

/* ---- Phase 2: card image ---- */

.post-card-image {
  display: block;
  width: calc(100% + var(--space-3) * 2);
  margin: calc(var(--space-3) * -1) calc(var(--space-3) * -1) var(--space-2);
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: var(--radius) var(--radius) 0 0;
  transition: transform var(--dur-base) var(--ease-out);
}

.post-card:hover .post-card-image {
  transform: scale(1.05);
}
```

(The negative margin bleeds the image out to the card's outer edge on all sides except the bottom, where `var(--space-2)` keeps normal spacing before the badge row. `.post-card` already has `overflow: hidden` from Phase 3, so the bled image is correctly clipped to the card's rounded corners.)

- [ ] **Step 3: Verify live in the browser**

Start both servers. Create a new post with an image (via `/posts/new`, from Task 3's work). Go to the Home page — confirm the new post's card shows the image at the top, flush with the card's edges, rounded only at the top corners. Hover the card — confirm the image zooms in slightly. Confirm posts without an image (all 12 seeded posts) still render exactly as before, no empty image box.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/PostCard.jsx frontend/src/components/PostCard.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Display uploaded image on PostCard with hover zoom"
```

---

### Task 5: Frontend — display image on PostDetail

**Files:**
- Modify: `frontend/src/pages/PostDetail.jsx` (targeted JSX change)
- Modify: `frontend/src/pages/PostDetail.css`

**Interfaces:** Consumes `API_URL` from `frontend/src/api/posts.js` (Task 3).

- [ ] **Step 1: Add the hero image to `frontend/src/pages/PostDetail.jsx`**

Find:
```jsx
import { getPost, deletePost } from '../api/posts'
```
Replace with:
```jsx
import { API_URL, getPost, deletePost } from '../api/posts'
```

Find:
```jsx
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h1>{post.title}</h1>
```
Replace with:
```jsx
      {post.image_url && (
        <img src={`${API_URL}${post.image_url}`} alt="" className="post-detail-image" />
      )}
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h1>{post.title}</h1>
```

(Everything else in the file stays the same.)

- [ ] **Step 2: Append to `frontend/src/pages/PostDetail.css`**

```css

/* ---- Phase 2: hero image ---- */

.post-detail-image {
  display: block;
  width: 100%;
  max-width: 680px;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: var(--radius);
  margin-bottom: var(--space-3);
}
```

- [ ] **Step 3: Verify live in the browser**

Start both servers. Open a post that has an image (created in Task 3/4's testing) — confirm a hero image renders above the category/country badges, sized consistently with the rest of the article's `680px` max-width column. Open a post with no image (any of the 12 seeded posts) — confirm it renders exactly as before, no gap, no broken image icon.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/PostDetail.jsx frontend/src/pages/PostDetail.css
git -c user.name="Valeri" -c user.email="absentminded193@gmail.com" commit -m "Display uploaded image on PostDetail"
```

---

### Task 6: Final verification and push

**Files:** none — this is a verification-and-push-only task.

**Interfaces:** none.

- [ ] **Step 1: Full end-to-end walkthrough**

Start both servers. Walk through, in order:
1. Create a new post with an image selected — confirm it appears on both the new post's detail page and its card on the Home page.
2. Edit that post and pick a *different* image — confirm the detail page now shows the new image, and (important) check `backend/uploads/` on disk to confirm the OLD image file is gone (only the new one remains for that post).
3. Edit that same post again but this time WITHOUT picking a new image (just change the title, say) — confirm the existing image is preserved (not lost) on save.
4. Delete that post — confirm (via `ls backend/uploads`) its image file is gone from disk.
5. Confirm a post with no image still creates/edits/displays/deletes correctly (the optional-ness of the whole feature).
6. Confirm the category/country filters, animations from Phase 3, and everything else built in prior phases still works normally (a quick sanity pass, not a full re-test).

- [ ] **Step 2: Commit and push**

If Step 1 required no code changes (expected — this task is verification only), there's nothing new to commit. Push whatever is currently unpushed from Tasks 1-5:

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
