# News Blog — Design Spec

Date: 2026-09-27

## Purpose

A mini full-stack project pulling together: Python basics, FastAPI, REST/CRUD,
SQLite + SQLAlchemy, and React (components/props/state/hooks/routing/fetch).
Backend and frontend are separate, independently runnable projects in one repo.

## Architecture

```
news-blog/
  backend/     FastAPI + SQLAlchemy + SQLite
  frontend/    React (Vite) + React Router
  README.md    setup + run instructions for both
```

No auth, no users — single-writer blog, CRUD only. Keeps scope tight (YAGNI);
easy to bolt on auth later if wanted.

## Data model

`Post`
- `id: int` (PK, autoincrement)
- `title: str`
- `content: str` (body, supports multiple paragraphs)
- `author: str`
- `category: str`
- `created_at: datetime` (server-set on create)
- `updated_at: datetime` (server-set on update)

Single table, no relationships/joins needed for a blog this size — keeps the
SQLAlchemy layer legible while still demonstrating engine/session/model setup
and full CRUD querying.

## Backend (FastAPI + SQLite + SQLAlchemy)

- `engine`/`SessionLocal`/`Base` in `database.py`, `Post` ORM model in `models.py`
- Pydantic schemas in `schemas.py`: `PostCreate`, `PostUpdate` (partial), `PostOut`
- Routes in `routers/posts.py`, mounted under `/posts`:
  - `GET /posts` — list all (newest first)
  - `GET /posts/{id}` — single post, 404 if missing
  - `POST /posts` — create, 201
  - `PUT /posts/{id}` — full update, 404 if missing
  - `DELETE /posts/{id}` — delete, 204
- CORS enabled for the Vite dev origin
- Swagger UI at `/docs` (free from FastAPI)
- `uvicorn` entrypoint in `main.py`

## Frontend (React + Vite + React Router)

Design direction: dark, modern editorial/magazine feel — not a default CRUD
form. Hero section, card-based post grid, real typography (Google Font),
smooth hover/transition states, consistent spacing system. Plain CSS
(no framework) so the styling itself is part of the demonstration.

Pages (React Router):
- `/` — Home: hero + grid of post cards (title, author, category, excerpt)
- `/posts/:id` — Post detail (full content) with Edit/Delete actions
- `/posts/new` — Create form
- `/posts/:id/edit` — Edit form

Structure:
- `src/api/posts.js` — fetch wrapper for the 5 endpoints
- `src/components/` — `Navbar`, `PostCard`, `PostForm` (shared by create/edit)
- `src/pages/` — `Home`, `PostDetail`, `NewPost`, `EditPost`
- State via `useState`/`useEffect` in pages, no global state library (not
  needed at this scale)

## Error handling

- Backend: 404 for missing post on get/update/delete; 422 auto from Pydantic
  validation on bad input.
- Frontend: loading state while fetching, inline error message on failed
  fetch/submit, simple confirm before delete.

## Testing

- Manual verification: run backend, hit `/docs`, exercise all 5 endpoints;
  run frontend, walk through list → view → create → edit → delete in browser.
- No automated test suite — out of scope for this mini project.

## Out of scope

Auth/users, comments, image uploads, search/pagination, tags, deployment.
