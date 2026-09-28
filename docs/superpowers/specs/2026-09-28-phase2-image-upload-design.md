# Phase 2: Image Upload — Design Spec

Date: 2026-09-28

## Purpose

Phase 2 of the multi-phase feature expansion (Phase 1: country/category
filters, done. Phase 3: animated design system, done — built out of
order since the project owner asked for the animation work first). This
phase adds an optional image to posts: upload from your computer,
stored on the backend, displayed on cards and the detail page.

## Goal

Let a post optionally carry one image, uploaded as a real file (not a
URL paste), stored on disk, served by FastAPI's `StaticFiles`, and shown
on the post card (with a hover zoom, consistent with the Phase 3
animation system) and the detail page. Posts without an image render
exactly as they do today — no placeholder box, no broken-image icon.

## Data model

Add one nullable column to the existing `Post` model:
- `image_url: str | None` — a relative URL like `/uploads/<uuid>.jpg`,
  or `None` for a post with no image. Plain nullable string, no foreign
  key, no separate images table — the upload endpoint is a stateless
  file-in/URL-out operation, not a tracked resource with its own
  lifecycle beyond "a file exists at this path or it doesn't."

## Backend

**Storage:** `backend/uploads/` — a new directory, created at startup if
missing, gitignored (added to `backend/.gitignore` alongside the
existing `venv/`, `__pycache__/`, `*.pyc`, `*.db` entries — uploaded
files are user-generated content, not source).

**Upload endpoint:** `POST /uploads/image` — accepts `multipart/form-data`
with a `file` field. Validates:
- Content type is one of `image/jpeg`, `image/png`, `image/webp`,
  `image/gif` (422 with a clear message otherwise).
- Size does not exceed 5MB (422 otherwise).

Saves the file under a generated UUID filename (preserving the original
extension) to avoid collisions and avoid trusting user-supplied
filenames. Returns `{"url": "/uploads/<uuid>.<ext>"}`.

**Serving:** `app.mount("/uploads", StaticFiles(directory="uploads"),
name="uploads")` in `main.py`, so an uploaded file is immediately
reachable at `http://localhost:8000/uploads/<filename>`.

**Cleanup:** this endpoint is decoupled from post create/update (a file
can be uploaded before the post it belongs to is saved), so file
lifecycle is managed by the post endpoints instead:
- `DELETE /posts/{id}` — if the post has an `image_url`, delete the
  corresponding file from `backend/uploads/` (best-effort: a missing
  file is not an error, deleting the post record still succeeds).
- `PUT /posts/{id}` — if the incoming `image_url` differs from the
  post's current one, delete the old file (same best-effort handling).

**Schema:** `PostBase` gains `image_url: str | None = None`, flowing
into `PostCreate`/`PostUpdate`/`PostOut` automatically.

## Frontend

**`api/uploads.js`** (new file) — exports `uploadImage(file)`, POSTing
a `FormData` multipart body to `/uploads/image`, returning `{ url }` on
success or throwing with a readable error message on failure (matching
the existing `handleResponse` error pattern in `api/posts.js`).

**`PostForm`** gains an image field:
- A file picker (styled, not the raw browser file input — matches the
  existing custom-control treatment already used for the country
  checkboxes).
- A live preview of the selected file (via `URL.createObjectURL`)
  before submit.
- When editing an existing post that already has an image, that image
  shows as the initial preview.
- On submit: if a new file was picked, it's uploaded first (via
  `uploadImage`), and the returned URL is what gets sent as
  `image_url` in the create/update payload. If editing and no new file
  was picked, the post's existing `image_url` is sent unchanged (no
  re-upload). The image is optional — submitting with no file sends
  `image_url: null`.

**`PostCard`** — if `post.image_url` is set, renders the image at the
top of the card (fixed aspect ratio, `object-fit: cover`, rounded top
corners matching the card), with a subtle scale-up on hover. If not
set, the card renders exactly as it does today (no reserved image
space, no placeholder).

**`PostDetail`** — same presence/absence logic, larger hero image above
the title when present.

Both card and detail images build their `src` from the backend's
`API_URL` (already defined in `api/posts.js`) plus the relative
`image_url` returned by the backend.

## Out of scope

Multiple images per post. Image cropping/editing in the browser. A
"remove image" action distinct from "upload a different image" (editing
without picking a new file always keeps the current one — there's no
UI path to explicitly clear an image once set, matching the scope the
project owner asked for). Seeding the 12 existing demo posts with
images (would require sourcing/generating stock images, outside what
was asked). Cloud/object storage (local disk is appropriate for this
project's scope).

## Testing

Manual/browser verification, consistent with the rest of this project:
curl the upload endpoint directly with a sample image, then browser-test
the full flow — create a post with an image, confirm it displays on the
card and detail page; edit a post to add/replace an image, confirm the
old file is gone from `backend/uploads/`; delete a post with an image,
confirm its file is gone too.
