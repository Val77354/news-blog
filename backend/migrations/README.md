# Database migrations

The server applies these automatically on startup (`app/migrations.py`).

To change the database:
1. Edit `app/models.py`.
2. Add a new file in `versions/`, copying the pattern of the latest one
   (bump `revision` and set `down_revision` to the previous one).
3. Restart the server, or run `python -m alembic upgrade head`.
