"""Test setup: a throwaway database and uploads folder, never the real ones."""

import os
import tempfile
from pathlib import Path

import pytest

_tmp = Path(tempfile.mkdtemp(prefix="newsblog-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp / 'test.db'}"
os.environ["UPLOAD_DIR"] = str(_tmp / "uploads")
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ENABLE_DOCS"] = "true"

from fastapi.testclient import TestClient  # noqa: E402

from app import security  # noqa: E402
from app.config import settings  # noqa: E402
from app.database import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.migrations import run_migrations  # noqa: E402
from app.routers import posts as posts_router  # noqa: E402

PASSWORD = "correct horse battery staple"
object.__setattr__(settings, "admin_password_hash", security.hash_password(PASSWORD))

CSRF = {"X-Requested-With": "XMLHttpRequest"}


@pytest.fixture(autouse=True)
def fresh_db():
    # Build each test's database from scratch with the real migrations.
    engine.dispose()
    for suffix in ("", "-wal", "-shm"):
        (_tmp / f"test.db{suffix}").unlink(missing_ok=True)
    run_migrations()
    security._failures.clear()
    posts_router._recent_views.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin(client):
    res = client.post("/auth/login", json={"password": PASSWORD}, headers=CSRF)
    assert res.status_code == 200
    return client


POST = {
    "title": "A test headline",
    "content": "Some body text.",
    "author": "Tester",
    "category": "World",
    "country": "France",
    "image_url": None,
}

PODCAST = {
    "title": "Test Pod",
    "host": "Host",
    "description": "About things.",
    "cover_image_url": None,
    "source": "Spotify",
    "external_url": "https://open.spotify.com/show/abc",
}
