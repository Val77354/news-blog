"""Admin login: password hashing, signed session cookies, and the guards
that protect every create/edit/delete endpoint.

How it works:
- Your password is never stored, only a scrypt hash of it (in .env).
- After login the browser gets an HttpOnly cookie that JavaScript can't read,
  signed with SECRET_KEY so it can't be forged, and expiring after SESSION_HOURS.
- Every write request must also send the header `X-Requested-With`. Browsers
  only let our own frontend (the allowed CORS origin) send it, which blocks
  cross-site request forgery.
- Too many wrong passwords from one IP address cause a temporary lockout.
"""

import base64
import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request, Response, status

from .config import log, settings

COOKIE_NAME = "dc_admin"
CSRF_HEADER = "x-requested-with"

# ---------- Password hashing (scrypt, from the standard library) ----------

_SCRYPT = {"n": 2**15, "r": 8, "p": 1, "maxmem": 64 * 1024 * 1024}


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, digest_hex = stored.split("$")
        if scheme != "scrypt":
            return False
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), **_SCRYPT)
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)


# ---------- Signed session tokens ----------

def _sign(message: str) -> str:
    mac = hmac.new(settings.secret_key.encode(), message.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")


def create_session_token() -> str:
    expires = int(time.time()) + settings.session_hours * 3600
    message = f"admin.{expires}"
    return f"{message}.{_sign(message)}"


def is_valid_session_token(token: str | None) -> bool:
    if not token:
        return False
    try:
        role, expires, signature = token.split(".")
        expires_at = int(expires)
    except ValueError:
        return False
    if role != "admin" or expires_at < time.time():
        return False
    return hmac.compare_digest(signature, _sign(f"{role}.{expires}"))


def set_session_cookie(response: Response) -> None:
    response.set_cookie(
        COOKIE_NAME,
        create_session_token(),
        max_age=settings.session_hours * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", secure=settings.cookie_secure, httponly=True, samesite="strict")


# ---------- Login rate limiting ----------

MAX_FAILURES = 5
LOCKOUT_SECONDS = 15 * 60
_failures: dict[str, deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def check_not_locked_out(request: Request) -> None:
    attempts = _failures[_client_ip(request)]
    now = time.time()
    while attempts and attempts[0] < now - LOCKOUT_SECONDS:
        attempts.popleft()
    if len(attempts) >= MAX_FAILURES:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many failed attempts. Try again in 15 minutes.")


def record_failed_login(request: Request) -> None:
    ip = _client_ip(request)
    _failures[ip].append(time.time())
    log.warning("Failed admin login from %s", ip)


def reset_failed_logins(request: Request) -> None:
    _failures.pop(_client_ip(request), None)


# ---------- Guards used by the routers ----------

def require_csrf_header(request: Request) -> None:
    if request.headers.get(CSRF_HEADER) != "XMLHttpRequest":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Missing X-Requested-With header.")


def is_admin(request: Request) -> bool:
    return is_valid_session_token(request.cookies.get(COOKIE_NAME))


def require_admin(request: Request, _csrf: None = Depends(require_csrf_header)) -> None:
    if not is_admin(request):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please log in as admin.")
