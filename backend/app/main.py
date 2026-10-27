from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .config import settings
from .database import engine
from .routers import auth, podcasts, posts, uploads
from .security import CSRF_HEADER

models.Base.metadata.create_all(bind=engine)
settings.upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="The Daily Current API",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
)

MAX_BODY_BYTES = settings.max_upload_bytes + 512 * 1024  # image plus form overhead
DOCS_PATHS = ("/docs", "/openapi.json")


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Refuse oversized requests before reading them.
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse({"detail": "Request is too large."}, status_code=413)

    response = await call_next(request)

    headers = response.headers
    headers["X-Content-Type-Options"] = "nosniff"
    headers["X-Frame-Options"] = "DENY"
    headers["Referrer-Policy"] = "no-referrer"
    headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not request.url.path.startswith(DOCS_PATHS):
        # The API only returns JSON and images, so it never needs to run scripts.
        headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if request.url.path.startswith("/uploads/"):
        headers["Cross-Origin-Resource-Policy"] = "cross-origin"  # the frontend shows these images
        headers["Cache-Control"] = "public, max-age=31536000, immutable"  # filenames never change
    else:
        headers["Cache-Control"] = "no-store"
    if settings.cookie_secure:
        headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,  # needed for the admin login cookie
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", CSRF_HEADER],
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(podcasts.router)
# The upload router must come BEFORE the /uploads static mount, because the
# mount claims every /uploads/* path and would otherwise swallow POST /uploads/image.
app.include_router(uploads.router)
app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "service": "news-blog-api"}
