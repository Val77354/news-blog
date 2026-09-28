from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .routers import posts, uploads
from .routers.uploads import UPLOAD_DIR

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="News Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
# uploads.router (POST /uploads/image) MUST be included before the
# StaticFiles mount below — Starlette matches routes in registration
# order, and Mount("/uploads", ...) claims the entire /uploads/* prefix.
# If this mount line ever moves above the include_router call, every
# upload silently starts returning 405 with no startup error.
app.include_router(uploads.router)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def read_root():
    return {"status": "ok", "service": "news-blog-api"}
