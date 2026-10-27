# Putting The Daily Current online

A checklist for when you're ready to go live. Nothing here is needed to run the site on your own PC.

## 1. Pick a host
The simplest setup is **one small Linux server (VPS)** running both parts, with
[Caddy](https://caddyserver.com) in front. Caddy gets HTTPS certificates automatically.

Use two addresses on the **same domain**, for example:
- `https://dailycurrent.example.com` for the website (the built frontend)
- `https://api.dailycurrent.example.com` for the backend

They must share the main domain, because the admin login cookie is `SameSite=Strict`.

## 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.production.example .env    # then edit the addresses
python set_password.py              # adds your password hash + secret key
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```
- Keep `--workers 1`: SQLite with one worker is simple and reliable for a blog.
- The database tables are created and updated automatically on startup.
- Run it as a service (systemd) so it restarts after a reboot.
- On startup the server warns if `COOKIE_SECURE`, `ENABLE_DOCS` or `CORS_ORIGINS`
  look wrong for an HTTPS site. Check the log.

## 3. Frontend
```bash
cd frontend
cp .env.production.example .env.production   # set VITE_API_URL
npm ci && npm run build                      # creates frontend/dist
```
Serve `frontend/dist` as static files. Every unknown path must fall back to
`index.html`, so links like `/posts/some-story` work.

## 4. Example Caddyfile
```
dailycurrent.example.com {
    root * /srv/dailycurrent/frontend/dist
    try_files {path} /index.html
    file_server
}

api.dailycurrent.example.com {
    reverse_proxy 127.0.0.1:8000
}
```

## 5. Backups
Add a daily cron job: `0 3 * * * /srv/dailycurrent/backend/venv/bin/python /srv/dailycurrent/backend/backup.py`.
Copy the backup folder off the server now and then, or sync it to cloud storage.

## 6. Final checks
- [ ] `https://` works and `http://` redirects to it (Caddy does this)
- [ ] `/docs` on the API returns 404
- [ ] Logging in works, and logging out hides the edit buttons
- [ ] `https://api…/feed.xml` and `/sitemap.xml` show your real site address
- [ ] Submit the sitemap in Google Search Console
