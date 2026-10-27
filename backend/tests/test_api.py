import io

import pytest
from fastapi.testclient import TestClient

from PIL import Image

from app.config import settings
from app.main import app

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
    assert client.get("/api/health").json()["status"] == "ok"


def test_public_can_read(admin, client):
    admin.post("/api/posts", json=POST, headers=CSRF)
    client.cookies.clear()
    assert len(client.get("/api/posts").json()) == 1
    assert client.get("/api/posts/1").json()["title"] == POST["title"]
    assert client.get("/api/posts/999").status_code == 404


def test_dates_are_utc(admin):
    created = admin.post("/api/posts", json=POST, headers=CSRF).json()
    assert created["created_at"].endswith(("Z", "+00:00"))


# ---------- Login and protection ----------

def test_writes_need_login(client):
    for method, url in [("post", "/api/posts"), ("put", "/api/posts/1"), ("delete", "/api/posts/1"),
                        ("post", "/api/podcasts"), ("put", "/api/podcasts/1"), ("delete", "/api/podcasts/1")]:
        kwargs = {"json": POST if "posts" in url else PODCAST} if method != "delete" else {}
        res = getattr(client, method)(url, headers=CSRF, **kwargs)
        assert res.status_code == 401, (method, url)
    files = {"file": ("a.png", _png_bytes(), "image/png")}
    assert client.post("/api/uploads/image", files=files, headers=CSRF).status_code == 401


def test_wrong_password(client):
    res = client.post("/api/auth/login", json={"password": "nope"}, headers=CSRF)
    assert res.status_code == 401
    assert client.get("/api/auth/me").json() == {"admin": False}


def test_lockout_after_repeated_failures(client):
    for _ in range(5):
        client.post("/api/auth/login", json={"password": "nope"}, headers=CSRF)
    res = client.post("/api/auth/login", json={"password": PASSWORD}, headers=CSRF)
    assert res.status_code == 429


def test_login_cookie_is_locked_down(client):
    res = client.post("/api/auth/login", json={"password": PASSWORD}, headers=CSRF)
    cookie = res.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie
    assert client.get("/api/auth/me").json() == {"admin": True}


def test_logout(admin):
    admin.post("/api/auth/logout", headers=CSRF)
    admin.cookies.clear()  # the test client keeps cookies; the browser obeys the delete
    assert admin.get("/api/auth/me").json() == {"admin": False}


def test_forged_cookie_rejected(client):
    client.cookies.set("dc_admin", "admin.9999999999.fakesignature")
    assert client.post("/api/posts", json=POST, headers=CSRF).status_code == 401


def test_csrf_header_required(admin):
    assert admin.post("/api/posts", json=POST).status_code == 403


# ---------- Validation ----------

def test_rejects_dangerous_links(admin):
    for bad in ["javascript:alert(1)", "data:text/html,hi", "//evil.com/x.png", "/uploads/../../secret"]:
        res = admin.post("/api/posts", json={**POST, "image_url": bad}, headers=CSRF)
        assert res.status_code == 422, bad
    res = admin.post("/api/podcasts", json={**PODCAST, "external_url": "javascript:alert(1)"}, headers=CSRF)
    assert res.status_code == 422


def test_rejects_bad_fields(admin):
    assert admin.post("/api/posts", json={**POST, "category": "Nonsense"}, headers=CSRF).status_code == 422
    assert admin.post("/api/posts", json={**POST, "title": "x" * 201}, headers=CSRF).status_code == 422
    assert admin.post("/api/posts", json={**POST, "is_admin": True}, headers=CSRF).status_code == 422
    assert admin.post("/api/posts", json={**POST, "title": "   "}, headers=CSRF).status_code == 422


def test_blank_image_becomes_none(admin):
    res = admin.post("/api/posts", json={**POST, "image_url": ""}, headers=CSRF)
    assert res.status_code == 201 and res.json()["image_url"] is None


def test_search_treats_percent_literally(admin):
    admin.post("/api/posts", json=POST, headers=CSRF)
    assert admin.get("/api/posts", params={"q": "%"}).json() == []
    assert len(admin.get("/api/posts", params={"q": "headline"}).json()) == 1


def test_pagination(admin):
    for i in range(3):
        admin.post("/api/posts", json={**POST, "title": f"Headline {i}"}, headers=CSRF)
    assert len(admin.get("/api/posts", params={"limit": 2}).json()) == 2
    assert admin.get("/api/posts", params={"limit": 1000}).status_code == 422


# ---------- Uploads ----------

def test_upload_is_cleaned_and_stripped(admin):
    files = {"file": ("photo.jpg", _png_bytes(exif_gps=True), "image/jpeg")}
    res = admin.post("/api/uploads/image", files=files, headers=CSRF)
    assert res.status_code == 201
    url = res.json()["url"]
    assert url.endswith(".webp")
    with Image.open(settings.upload_dir / url.removeprefix("/uploads/")) as img:
        assert not img.getexif()


def test_upload_rejects_fake_image(admin):
    files = {"file": ("evil.png", b"<script>alert(1)</script>", "image/png")}
    assert admin.post("/api/uploads/image", files=files, headers=CSRF).status_code == 422


def test_shared_image_not_deleted(admin):
    url = admin.post("/api/uploads/image", files={"file": ("a.png", _png_bytes(), "image/png")}, headers=CSRF).json()["url"]
    path = settings.upload_dir / url.removeprefix("/uploads/")
    admin.post("/api/posts", json={**POST, "image_url": url}, headers=CSRF)
    admin.post("/api/posts", json={**POST, "image_url": url}, headers=CSRF)
    admin.delete("/api/posts/2", headers=CSRF)
    assert path.exists()  # post 1 still uses it
    admin.delete("/api/posts/1", headers=CSRF)
    assert not path.exists()  # now nobody does


def test_podcast_cover_cleaned_up(admin):
    url = admin.post("/api/uploads/image", files={"file": ("a.png", _png_bytes(), "image/png")}, headers=CSRF).json()["url"]
    admin.post("/api/podcasts", json={**PODCAST, "cover_image_url": url}, headers=CSRF)
    admin.delete("/api/podcasts/1", headers=CSRF)
    assert not (settings.upload_dir / url.removeprefix("/uploads/")).exists()


# ---------- Headers ----------

def test_security_headers(client):
    headers = client.get("/api/posts").headers
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in headers["content-security-policy"]


def test_cors_only_allows_frontend(client):
    ok = client.options("/api/posts", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    bad = client.options("/api/posts", headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in bad.headers


# ---------- Drafts ----------

def test_drafts_hidden_from_visitors(admin, client):
    admin.post("/api/posts", json={**POST, "title": "Secret draft", "status": "draft"}, headers=CSRF)
    admin.post("/api/posts", json=POST, headers=CSRF)
    assert len(admin.get("/api/posts").json()) == 2  # admin sees both
    admin.cookies.clear()
    visible = client.get("/api/posts").json()
    assert [p["title"] for p in visible] == [POST["title"]]
    assert client.get("/api/posts/1").status_code == 404
    assert client.get("/api/posts/secret-draft").status_code == 404


def test_publishing_a_draft_sets_date(admin):
    draft = admin.post("/api/posts", json={**POST, "status": "draft"}, headers=CSRF).json()
    assert draft["published_at"] is None
    published = admin.put(f"/api/posts/{draft['id']}", json={**POST, "status": "published"}, headers=CSRF).json()
    assert published["published_at"] is not None


# ---------- Slugs ----------

def test_slugs(admin):
    first = admin.post("/api/posts", json={**POST, "title": "Zürich Hosts Talks!"}, headers=CSRF).json()
    second = admin.post("/api/posts", json={**POST, "title": "Zurich hosts talks"}, headers=CSRF).json()
    assert first["slug"] == "zurich-hosts-talks"
    assert second["slug"] == "zurich-hosts-talks-2"
    assert admin.get("/api/posts/zurich-hosts-talks").json()["id"] == first["id"]
    assert admin.get(f"/api/posts/{first['id']}").json()["slug"] == first["slug"]  # old number links still work
    edited = admin.put(f"/api/posts/{first['id']}", json={**POST, "title": "New title"}, headers=CSRF).json()
    assert edited["slug"] == "zurich-hosts-talks"  # links don't break when the title changes


# ---------- View counts ----------

def test_views_count_once_per_visitor(admin, client):
    post = admin.post("/api/posts", json=POST, headers=CSRF).json()
    assert admin.post(f"/api/posts/{post['id']}/view", headers=CSRF).json()["view_count"] == 0  # admin not counted
    admin.cookies.clear()
    assert client.post(f"/api/posts/{post['id']}/view", headers=CSRF).json()["view_count"] == 1
    assert client.post(f"/api/posts/{post['id']}/view", headers=CSRF).json()["view_count"] == 1  # repeat ignored
    after = client.get(f"/api/posts/{post['id']}").json()
    assert after["view_count"] == 1 and after["updated_at"] == post["updated_at"]


# ---------- Full-text search ----------

def test_full_text_search(admin):
    admin.post("/api/posts", json={**POST, "title": "Geneva privacy talks", "content": "Negotiators met."}, headers=CSRF)
    admin.post("/api/posts", json={**POST, "title": "Football final", "content": "A late goal in Genève."}, headers=CSRF)
    titles = lambda q: [p["title"] for p in admin.get("/api/posts", params={"q": q}).json()]  # noqa: E731
    assert titles("privacy") == ["Geneva privacy talks"]
    assert titles("negotiat") == ["Geneva privacy talks"]  # matches the start of a word
    assert titles("geneve") == ["Football final"]  # accents ignored
    assert titles("geneva talks") == ["Geneva privacy talks"]  # every word must match
    assert titles('"); DROP TABLE posts; --') == []  # odd input is harmless
    admin.put("/api/posts/1", json={**POST, "title": "Renamed"}, headers=CSRF)
    assert titles("privacy") == []  # index follows edits


# ---------- Own images only ----------

def test_outside_images_rejected_but_old_ones_kept(admin):
    outside = "https://picsum.photos/seed/x/800/450"
    assert admin.post("/api/posts", json={**POST, "image_url": outside}, headers=CSRF).status_code == 422
    assert admin.post("/api/podcasts", json={**PODCAST, "cover_image_url": outside}, headers=CSRF).status_code == 422
    # A post that already had an outside image (from before this rule) can still be edited.
    from app.database import SessionLocal
    from app.models import Post
    with SessionLocal() as db:
        db.add(Post(**{**POST, "image_url": outside}, slug="old-post", status="published"))
        db.commit()
    assert admin.put("/api/posts/1", json={**POST, "image_url": outside, "title": "Edited"}, headers=CSRF).status_code == 200
    assert admin.put("/api/posts/1", json={**POST, "image_url": outside + "?new"}, headers=CSRF).status_code == 422


# ---------- Feeds ----------

def test_rss_and_sitemap(admin):
    admin.post("/api/posts", json={**POST, "title": "Public <story> & more"}, headers=CSRF)
    admin.post("/api/posts", json={**POST, "title": "Hidden draft", "status": "draft"}, headers=CSRF)
    rss = admin.get("/feed.xml")
    assert rss.headers["content-type"].startswith("application/rss+xml")
    assert "Public &lt;story&gt; &amp; more" in rss.text and "Hidden draft" not in rss.text
    sitemap = admin.get("/sitemap.xml").text
    assert "/posts/public-story-more" in sitemap and "/api/" not in sitemap and "hidden-draft" not in sitemap


# ---------- Stricter validation ----------

def test_names_reject_numbers_and_symbols(admin):
    for bad in ["4nna", "Anna_99", "<b>Anna</b>", "Anna!!", "a@b.com", "J"]:
        res = admin.post("/api/posts", json={**POST, "author": bad}, headers=CSRF)
        assert res.status_code == 422, bad
    for good in ["Dr. Priya Nair", "Piotr Zieliński", "Anna O'Neil-Smith", "Élise Fontaine"]:
        res = admin.post("/api/posts", json={**POST, "author": good, "title": f"Story by {good}"}, headers=CSRF)
        assert res.status_code == 201, good
    assert admin.post("/api/podcasts", json={**PODCAST, "host": "Host 2000"}, headers=CSRF).status_code == 422


def test_titles_and_text_need_real_words(admin):
    for bad_title in ["12345", "!!!???", "a\nb c d", "ok\x00title"]:
        assert admin.post("/api/posts", json={**POST, "title": bad_title}, headers=CSRF).status_code == 422, bad_title
    assert admin.post("/api/posts", json={**POST, "content": "1234567890 !!"}, headers=CSRF).status_code == 422
    assert admin.post("/api/posts", json={**POST, "content": "Too short"}, headers=CSRF).status_code == 422


def test_validation_message_names_the_problem(admin):
    detail = admin.post("/api/posts", json={**POST, "author": "R2D2"}, headers=CSRF).json()["detail"]
    assert detail[0]["loc"][-1] == "author" and "numbers or symbols" in detail[0]["msg"]


# ---------- Error handling ----------

def test_unexpected_errors_are_hidden_and_logged(client, monkeypatch, caplog):
    from app.routers import posts as posts_router

    def boom(*args, **kwargs):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(posts_router, "_visible_to", boom)
    safe_client = TestClient(app, raise_server_exceptions=False)
    res = safe_client.get("/api/posts")
    assert res.status_code == 500
    assert "secret" not in res.text and "went wrong" in res.json()["detail"]
    assert "secret internal detail" in caplog.text


def test_delete_post_by_id(admin):
    post = admin.post("/api/posts", json=POST, headers=CSRF).json()
    assert admin.delete(f"/api/posts/{post['id']}", headers=CSRF).status_code == 204
    assert admin.get(f"/api/posts/{post['slug']}").status_code == 404


# ---------- One address for site + API ----------

def test_website_served_with_page_fallback(client, tmp_path, monkeypatch):
    if not (settings.frontend_dist / "index.html").exists():
        pytest.skip("frontend not built")
    home = client.get("/")
    assert home.status_code == 200 and '<div id="root">' in home.text
    deep = client.get("/posts/some-story")  # a React page, not an API call
    assert deep.status_code == 200 and '<div id="root">' in deep.text
    assert "script-src 'self'" in deep.headers["content-security-policy"]
    assert client.get("/api/does-not-exist").status_code == 404
    assert client.get("/../backend/.env").status_code in (200, 404) and "SECRET" not in client.get("/../backend/.env").text


# ---------- News import ----------

RSS = b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>
  <title>Example News</title>
  <item><title>Parliament passes &lt;b&gt;budget&lt;/b&gt;</title><link>https://news.example.com/budget</link>
    <description>&lt;p&gt;Lawmakers approved the spending plan after a long debate.&lt;/p&gt;</description>
    <dc:creator>Maria Lopez</dc:creator></item>
  <item><title>2024</title><link>https://news.example.com/numbers</link><description>Only numbers here.</description></item>
  <item><title>Storm hits coast</title><link>https://news.example.com/storm</link>
    <description>Heavy winds and rain caused flooding along the northern coast overnight.</description>
    <dc:creator>@weather_bot 99</dc:creator></item>
</channel></rss>"""


def _fake_download(monkeypatch, data=RSS):
    from app import news_import
    monkeypatch.setattr(news_import, "download_feed", lambda url: data)


def test_import_creates_drafts(admin, client, monkeypatch):
    _fake_download(monkeypatch)
    body = {"feed_url": "https://news.example.com/rss", "category": "World", "country": "France"}
    res = admin.post("/api/import", json=body, headers=CSRF).json()
    titles = [p["title"] for p in res["created"]]
    assert titles == ["Parliament passes budget", "Storm hits coast"]  # HTML removed
    assert res["skipped"] == ["2024"]  # not a real headline
    first, second = res["created"]
    assert first["status"] == "draft" and first["author"] == "Maria Lopez"
    assert first["source_url"] == "https://news.example.com/budget"
    assert "<p>" not in first["content"] and "Lawmakers approved" in first["content"]
    assert second["author"] == "Example News"  # invalid author name replaced by the feed's name
    # Running it again doesn't create duplicates.
    again = admin.post("/api/import", json=body, headers=CSRF).json()
    assert again["created"] == [] and again["already_imported"] == 2
    # Visitors don't see the drafts.
    admin.cookies.clear()
    assert client.get("/api/posts").json() == []


def test_import_needs_admin(client):
    body = {"feed_url": "https://news.example.com/rss", "category": "World", "country": "France"}
    assert client.post("/api/import", json=body, headers=CSRF).status_code == 401


def test_import_blocks_private_addresses(admin):
    for url in ["http://127.0.0.1:8000/api/posts", "http://localhost/", "http://192.168.1.1/feed", "http://[::1]/"]:
        body = {"feed_url": url, "category": "World", "country": "France"}
        res = admin.post("/api/import", json=body, headers=CSRF)
        assert res.status_code == 400 and "private" in res.json()["detail"], url


def test_import_rejects_non_feeds_and_xml_bombs(admin, monkeypatch):
    body = {"feed_url": "https://news.example.com/rss", "category": "World", "country": "France"}
    _fake_download(monkeypatch, b"<html><body>Just a web page</body></html>")
    assert "valid RSS" in admin.post("/api/import", json=body, headers=CSRF).json()["detail"]
    bomb = b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;">]><rss>&b;</rss>'
    _fake_download(monkeypatch, bomb)
    assert admin.post("/api/import", json=body, headers=CSRF).status_code == 400
