# Putting The Daily Current online

A checklist for when you're ready to go live. You don't need any of this to run the site on your own PC.

## 1. Pick a host
The backend serves the website **and** the API from one address, so you only
need **one small Linux server (VPS)** with one domain, e.g. `https://dailycurrent.example.com`.
Put [Caddy](https://caddyserver.com) in front; it gets HTTPS certificates automatically.

## 2. Build and start
```bash
# website
cd frontend
npm ci && npm run build            # creates frontend/dist, served by the backend

# backend
cd ../backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.production.example .env    # then edit the addresses
python set_password.py             # adds your password hash + secret key
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```
- Keep `--workers 1`: SQLite with one worker is simple and reliable for a blog.
- The database tables are created and upgraded automatically on startup.
- Run it as a service (systemd) so it restarts after a reboot.
- On startup the server warns if `COOKIE_SECURE`, `ENABLE_DOCS` or `CORS_ORIGINS`
  look wrong for an HTTPS site. Check the log.

## 3. Caddyfile
```
dailycurrent.example.com {
    reverse_proxy 127.0.0.1:8000
}
```
That's all: the backend already serves pages, `/api`, images, `/feed.xml` and `/sitemap.xml`.

## 4. Backups and news import
Add cron jobs:
```
0 3 * * *   /srv/dailycurrent/backend/venv/bin/python /srv/dailycurrent/backend/backup.py
0 */6 * * * /srv/dailycurrent/backend/venv/bin/python /srv/dailycurrent/backend/import_news.py
```
The second line is optional: it collects news from `import_feeds.json` as drafts every 6 hours.
Copy the backup folder off the server now and then, or sync it to cloud storage.

## 5. Final checks
- [ ] `https://` works and `http://` redirects to it (Caddy does this)
- [ ] `/docs` returns the website's "page not found", not the API docs
- [ ] Logging in works, and logging out hides the edit buttons
- [ ] `/feed.xml` and `/sitemap.xml` show your real site address
- [ ] Submit the sitemap in Google Search Console
