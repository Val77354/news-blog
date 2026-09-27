# News Blog

A full-stack mini news blog: FastAPI + SQLite backend with complete CRUD,
and a React (Vite) frontend with a dark editorial design.

## Stack

- **Backend:** Python, FastAPI, Uvicorn, SQLAlchemy 2.0 (typed ORM), Pydantic v2, SQLite
- **Frontend:** React 18, Vite, React Router v6, plain CSS

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
python seed.py                 # optional: adds 5 sample posts
uvicorn app.main:app --reload --port 8000
```

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
| POST   | /posts        | Create a post        |
| PUT    | /posts/{id}   | Update a post        |
| DELETE | /posts/{id}   | Delete a post        |

## Design doc

See `docs/superpowers/specs/2026-09-27-news-blog-design.md` for the full design spec.
