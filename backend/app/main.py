"""The web server.

Everything lives on one address:
- /api/...                 the JSON API (and /api/uploads/... for images)
- /feed.xml, /sitemap.xml  for feed readers and search engines
- everything else          the website itself (the built React app in frontend/dist)
"""

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from .config import log, settings
from .migrations import run_migrations
from .routers import auth, feeds, importer, podcasts, posts, uploads
from .security import CSRF_HEADER

run_migrations()  # create or update the database tables
settings.upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="The Daily Current API",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
)

MAX_BODY_BYTES = settings.max_upload_bytes + 512 * 1024  # image plus form overhead
DOCS_PATHS = ("/docs", "/openapi.json")

# The website may load its own files, Google Fonts, and images (old posts use
# outside images). Everything else, including scripts from other sites, is blocked.
SITE_CSP = (
    "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; "
    "img-src 'self' data: blob: https:; connect-src 'self'; frame-ancestors 'none'"
)
# The API only returns JSON, XML and images, so it never needs to run anything.
API_CSP = "default-src 'none'; frame-ancestors 'none'"


def _is_api(path: str) -> bool:
    return path.startswith("/api/") or path in ("/feed.xml", "/sitemap.xml")


# ---------- Security headers ----------

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Refuse oversized requests before reading them.
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse({"detail": "Request is too large."}, status_code=413)

    response = await call_next(request)
    path = request.url.path

    headers = response.headers
    headers["X-Content-Type-Options"] = "nosniff"
    headers["X-Frame-Options"] = "DENY"
    headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not path.startswith(DOCS_PATHS):
        headers["Content-Security-Policy"] = API_CSP if _is_api(path) else SITE_CSP

    if path.startswith(("/api/uploads/", "/assets/")):
        headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        headers["Cache-Control"] = "public, max-age=31536000, immutable"  # file names never change
    elif "cache-control" not in headers:
        headers["Cache-Control"] = "no-store" if _is_api(path) else "no-cache"
    if settings.cookie_secure:
        headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# Only needed when the website is served from a different address (e.g. `npm run dev`
# without the proxy). When the backend serves the site itself, everything is same-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # needed for the admin login cookie
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", CSRF_HEADER],
)


# ---------- Error handling ----------

@app.exception_handler(IntegrityError)
async def integrity_error(request: Request, exc: IntegrityError):
    log.warning("Database conflict on %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse({"detail": "That conflicts with existing data. Please try again."}, status_code=409)


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    # Log the full details for you; show visitors a plain message with no internals.
    log.exception("Unexpected error on %s %s", request.method, request.url.path)
    return JSONResponse({"detail": "Something went wrong on our side. Please try again."}, status_code=500)


# ---------- Routes ----------

api = APIRouter(prefix="/api")
api.include_router(auth.router)
api.include_router(posts.router)
api.include_router(podcasts.router)
api.include_router(uploads.router)
api.include_router(importer.router)


@api.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "news-blog-api"}


app.include_router(api)
app.include_router(feeds.router)
# Must come after the routers: the mount claims every /api/uploads/* path, and
# POST /api/uploads/image has to be matched first.
app.mount("/api/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")


# ---------- The website ----------

dist = settings.frontend_dist
if (dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(dist / "assets")), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def website(path: str):
        if path.startswith("api/"):
            return JSONResponse({"detail": "Not found"}, status_code=404)
        file = (dist / path).resolve()
        if path and file.is_file() and file.is_relative_to(dist.resolve()):
            return FileResponse(file)  # e.g. favicon.ico, robots.txt
        # Every other address is a page of the React app (/, /posts/..., /podcasts, ...).
        return FileResponse(dist / "index.html")
else:
    log.warning("No built website at %s. Run `npm run build` in frontend/ to serve it from here.", dist)
