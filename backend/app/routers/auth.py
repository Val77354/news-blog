from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from ..config import settings
from ..schemas import AuthStatus, LoginIn
from ..security import (
    check_not_locked_out,
    clear_session_cookie,
    is_admin,
    record_failed_login,
    require_csrf_header,
    reset_failed_logins,
    set_session_cookie,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthStatus, dependencies=[Depends(require_csrf_header)])
def login(data: LoginIn, request: Request, response: Response):
    check_not_locked_out(request)
    if not settings.admin_password_hash or not verify_password(data.password, settings.admin_password_hash):
        record_failed_login(request)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong password.")
    reset_failed_logins(request)
    set_session_cookie(response)
    return {"admin": True}


@router.post("/logout", response_model=AuthStatus, dependencies=[Depends(require_csrf_header)])
def logout(response: Response):
    clear_session_cookie(response)
    return {"admin": False}


@router.get("/me", response_model=AuthStatus)
def me(request: Request):
    return {"admin": is_admin(request)}
