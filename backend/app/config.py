"""All settings in one place, read from environment variables or backend/.env.

Run `python set_password.py` once to create the .env file with your admin
password. See .env.example for every option.
"""

import logging
import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

log = logging.getLogger("news_blog")


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _list(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'news_blog.db'}")
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", str(BACKEND_DIR / "uploads")))
    # The built website (`npm run build`), served by the backend at /
    frontend_dist: Path = Path(os.getenv("FRONTEND_DIST", str(BACKEND_DIR.parent / "frontend" / "dist")))
    cors_origins: list[str] = field(default_factory=lambda: _list("CORS_ORIGINS", "http://localhost:5173"))
    # The public address of the website, used in the RSS feed and sitemap.
    site_url: str = os.getenv("SITE_URL", "http://localhost:5173").rstrip("/")

    # Admin login
    admin_password_hash: str = os.getenv("ADMIN_PASSWORD_HASH", "")
    secret_key: str = os.getenv("SECRET_KEY", "")
    session_hours: int = int(os.getenv("SESSION_HOURS", "12"))
    # Set to true when the site runs over HTTPS (it always should in production).
    cookie_secure: bool = _bool("COOKIE_SECURE", False)

    # Show the interactive API docs at /docs. Turn off in production.
    enable_docs: bool = _bool("ENABLE_DOCS", True)

    max_upload_bytes: int = 5 * 1024 * 1024


settings = Settings()

if not settings.secret_key:
    # Still works, but everyone gets logged out whenever the server restarts.
    log.warning("SECRET_KEY is not set; using a temporary one. Run `python set_password.py`.")
    object.__setattr__(settings, "secret_key", secrets.token_urlsafe(48))

if not settings.admin_password_hash:
    log.warning("ADMIN_PASSWORD_HASH is not set; admin login is disabled. Run `python set_password.py`.")

# Production safety checks: the site is "live" once it's served over https.
if settings.site_url.startswith("https://"):
    if not settings.cookie_secure:
        log.warning("Site is on HTTPS but COOKIE_SECURE is false. Set COOKIE_SECURE=true.")
    if settings.enable_docs:
        log.warning("API docs are public. Set ENABLE_DOCS=false in production.")
    if any(origin.startswith("http://") for origin in settings.cors_origins):
        log.warning("CORS_ORIGINS contains an http:// address. Use only your https:// site.")
