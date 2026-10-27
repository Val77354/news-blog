import io

from PIL import Image

from app.config import settings

from .conftest import CSRF, PASSWORD, PODCAST, POST


def _png_bytes(exif_gps: bool = False) -> bytes:
    img = Image.new("RGB", (40, 30), "red")
    out = io.BytesIO()
    if exif_gps:
        exif = Image.Exif()
        exif[0x8825] = {2: (51.0, 30.0, 0.0)}  # GPS latitude
        img.save(out, "JPEG", exif=exif)
    else:
        img.save(out, "PNG")
    return out.getvalue()


# ---------- Public reading ----------

def test_health(client):
    assert client.get("/").json()["status"] == "ok"


def test_public_can_read(admin, client):
    admin.post("/posts", json=POST, headers=CSRF)
    client.cookies.clear()
    assert len(client.get("/posts").json()) == 1
    assert client.get("/posts/1").json()["title"] == POST["title"]
    assert client.get("/posts/999").status_code == 404


def test_dates_are_utc(admin):
    created = admin.post("/posts", json=POST, headers=CSRF).json()
    assert created["created_at"].endswith(("Z", "+00:00"))


# ---------- Login and protection ----------

def test_writes_need_login(client):
    for method, url in [("post", "/posts"), ("put", "/posts/1"), ("delete", "/posts/1"),
                        ("post", "/podcasts"), ("put", "/podcasts/1"), ("delete", "/podcasts/1")]:
        kwargs = {"json": POST if "posts" in url else PODCAST} if method != "delete" else {}
        res = getattr(client, method)(url, headers=CSRF, **kwargs)
        assert res.status_code == 401, (method, url)
    files = {"file": ("a.png", _png_bytes(), "image/png")}
    assert client.post("/uploads/image", files=files, headers=CSRF).status_code == 401


def test_wrong_password(client):
    res = client.post("/auth/login", json={"password": "nope"}, headers=CSRF)
    assert res.status_code == 401
    assert client.get("/auth/me").json() == {"admin": False}


def test_lockout_after_repeated_failures(client):
    for _ in range(5):
        client.post("/auth/login", json={"password": "nope"}, headers=CSRF)
    res = client.post("/auth/login", json={"password": PASSWORD}, headers=CSRF)
    assert res.status_code == 429


def test_login_cookie_is_locked_down(client):
    res = client.post("/auth/login", json={"password": PASSWORD}, headers=CSRF)
    cookie = res.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie
    assert client.get("/auth/me").json() == {"admin": True}


def test_logout(admin):
    admin.post("/auth/logout", headers=CSRF)
    admin.cookies.clear()  # the test client keeps cookies; the browser obeys the delete
    assert admin.get("/auth/me").json() == {"admin": False}


def test_forged_cookie_rejected(client):
    client.cookies.set("dc_admin", "admin.9999999999.fakesignature")
    assert client.post("/posts", json=POST, headers=CSRF).status_code == 401


def test_csrf_header_required(admin):
    assert admin.post("/posts", json=POST).status_code == 403


# ---------- Validation ----------

def test_rejects_dangerous_links(admin):
    for bad in ["javascript:alert(1)", "data:text/html,hi", "//evil.com/x.png", "/uploads/../../secret"]:
        res = admin.post("/posts", json={**POST, "image_url": bad}, headers=CSRF)
        assert res.status_code == 422, bad
    res = admin.post("/podcasts", json={**PODCAST, "external_url": "javascript:alert(1)"}, headers=CSRF)
    assert res.status_code == 422


def test_rejects_bad_fields(admin):
    assert admin.post("/posts", json={**POST, "category": "Nonsense"}, headers=CSRF).status_code == 422
    assert admin.post("/posts", json={**POST, "title": "x" * 201}, headers=CSRF).status_code == 422
    assert admin.post("/posts", json={**POST, "is_admin": True}, headers=CSRF).status_code == 422
    assert admin.post("/posts", json={**POST, "title": "   "}, headers=CSRF).status_code == 422


def test_blank_image_becomes_none(admin):
    res = admin.post("/posts", json={**POST, "image_url": ""}, headers=CSRF)
    assert res.status_code == 201 and res.json()["image_url"] is None


def test_search_treats_percent_literally(admin):
    admin.post("/posts", json=POST, headers=CSRF)
    assert admin.get("/posts", params={"q": "%"}).json() == []
    assert len(admin.get("/posts", params={"q": "headline"}).json()) == 1


def test_pagination(admin):
    for i in range(3):
        admin.post("/posts", json={**POST, "title": f"Headline {i}"}, headers=CSRF)
    assert len(admin.get("/posts", params={"limit": 2}).json()) == 2
    assert admin.get("/posts", params={"limit": 1000}).status_code == 422


# ---------- Uploads ----------

def test_upload_is_cleaned_and_stripped(admin):
    files = {"file": ("photo.jpg", _png_bytes(exif_gps=True), "image/jpeg")}
    res = admin.post("/uploads/image", files=files, headers=CSRF)
    assert res.status_code == 201
    url = res.json()["url"]
    assert url.endswith(".webp")
    with Image.open(settings.upload_dir / url.removeprefix("/uploads/")) as img:
        assert not img.getexif()


def test_upload_rejects_fake_image(admin):
    files = {"file": ("evil.png", b"<script>alert(1)</script>", "image/png")}
    assert admin.post("/uploads/image", files=files, headers=CSRF).status_code == 422


def test_shared_image_not_deleted(admin):
    url = admin.post("/uploads/image", files={"file": ("a.png", _png_bytes(), "image/png")}, headers=CSRF).json()["url"]
    path = settings.upload_dir / url.removeprefix("/uploads/")
    admin.post("/posts", json={**POST, "image_url": url}, headers=CSRF)
    admin.post("/posts", json={**POST, "image_url": url}, headers=CSRF)
    admin.delete("/posts/2", headers=CSRF)
    assert path.exists()  # post 1 still uses it
    admin.delete("/posts/1", headers=CSRF)
    assert not path.exists()  # now nobody does


def test_podcast_cover_cleaned_up(admin):
    url = admin.post("/uploads/image", files={"file": ("a.png", _png_bytes(), "image/png")}, headers=CSRF).json()["url"]
    admin.post("/podcasts", json={**PODCAST, "cover_image_url": url}, headers=CSRF)
    admin.delete("/podcasts/1", headers=CSRF)
    assert not (settings.upload_dir / url.removeprefix("/uploads/")).exists()


# ---------- Headers ----------

def test_security_headers(client):
    headers = client.get("/posts").headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in headers["content-security-policy"]


def test_cors_only_allows_frontend(client):
    ok = client.options("/posts", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = client.options("/posts", headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in bad.headers
