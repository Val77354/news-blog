# News Blog

A full-stack mini news blog: FastAPI + SQLite backend with complete CRUD,
and a React (Vite) frontend with a dark editorial design.

## Stack

- **Backend:** Python, FastAPI, Uvicorn, SQLAlchemy 2.0 (typed ORM), Pydantic v2, SQLite
- **Frontend:** React 19, Vite, React Router v7, plain CSS

## Project structure

```
news-blog/
  backend/    FastAPI app (app/), seed script, requirements.txt
  frontend/   React app (src/), Vite config
```

## Running the backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash; use venv\Scripts\activate on cmd/PowerShell
pip install -r requirements.txt
python set_password.py         # choose your admin password (creates backend/.env)
python seed.py                 # optional: adds sample posts
uvicorn app.main:app --reload --port 8000
```

Run the tests with `pip install -r requirements-dev.txt` then `pytest`.

The database is created and upgraded automatically on startup (Alembic
migrations in `backend/migrations/`). On this PC it lives outside OneDrive, in
`C:\Users\Valeri\DailyCurrentData` (set in `backend/.env`), because syncing a
live SQLite file can corrupt it.

### Backups

`python backup.py` saves a checked copy of the database plus the uploads. It
runs every night at 3:00 through Windows Task Scheduler ("DailyCurrentBackup")
and keeps the newest 14 copies in `OneDrive\DailyCurrentBackups`, so there's
also a copy in the cloud. To restore, stop the backend and copy a backup over
the database file.

### Features
- **Drafts:** choose "Draft" in the post form; only the admin can see drafts.
- **Readable links:** `/posts/geneva-hosts-renewed-talks…` (old `/posts/12` links still work).
- **Real view counts:** each visitor counts once per post per 30 minutes; your own visits aren't counted.
- **Search:** SQLite full-text search; matches word starts, ignores accents, best matches first.
- **RSS feed** at `/feed.xml` and **sitemap** at `/sitemap.xml` on the API.
- **Images:** must be uploaded; links to images on other sites are refused (they let those sites track readers).

Going live? See `docs/DEPLOYMENT.md`.

### Admin login and security

Anyone can read the site, but creating, editing or deleting posts and
podcasts, and uploading images, needs the admin password. Log in at
`/login` (there's also an "Admin login" link in the footer).

- Only a scrypt hash of the password is stored, in `backend/.env` (never committed).
- The login is an HttpOnly, SameSite=Strict cookie signed with `SECRET_KEY`.
- Writes also require an `X-Requested-With` header, which blocks cross-site forgery.
- 5 wrong passwords lock that IP address out for 15 minutes.
- Inputs are validated strictly (lengths, fixed categories, http/https links only).
- Uploads are re-encoded to WebP, which strips GPS/EXIF data and rejects fake images.
- Security headers on every response; CORS allows only `CORS_ORIGINS`.

All options are listed in `backend/.env.example`. For production, set
`COOKIE_SECURE=true`, `ENABLE_DOCS=false`, `CORS_ORIGINS` to your site address,
and `VITE_API_URL` for the frontend build.

API docs (Swagger UI): http://localhost:8000/docs

## Running the frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

The frontend expects the backend running on `http://localhost:8000` (CORS is
already configured for `http://localhost:5173`).

## API

| Method | Path          | Description        |
|--------|---------------|---------------------|
| GET    | /posts        | List all posts      |
| GET    | /posts/{id}   | Get one post        |
| POST   | /posts        | Create a post (admin) |
| PUT    | /posts/{id}   | Update a post (admin) |
| DELETE | /posts/{id}   | Delete a post (admin) |
| GET/POST/PUT/DELETE | /podcasts… | Same pattern for podcasts |
| POST   | /uploads/image | Upload an image (admin) |
| POST   | /auth/login, /auth/logout | Admin login / logout |
| GET    | /auth/me      | Am I logged in?      |

List endpoints accept `limit` (max 100), `offset`, and `q` for search.

## Design doc

See `docs/superpowers/specs/2026-09-27-news-blog-design.md` for the full design spec.
