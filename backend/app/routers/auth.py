from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_session
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

_COOKIE_OPTS = dict(httponly=True, samesite="lax", secure=False)


def _set_auth_cookies(response: Response, user: User) -> None:
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    response.set_cookie("access_token", access_token, max_age=15 * 60, **_COOKIE_OPTS)
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=7 * 24 * 3600,
        path="/api/auth/refresh",
        **_COOKIE_OPTS,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, response: Response, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="email_taken")

    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    _set_auth_cookies(response, user)
    return user


@router.post("/login", response_model=UserResponse)
async def login(body: LoginRequest, response: Response, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid_credentials")

    _set_auth_cookies(response, user)
    return user


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return {"detail": "logged_out"}


@router.post("/refresh", response_model=UserResponse)
async def refresh(
    response: Response,
    refresh_token: str = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="token_missing")

    user_id = decode_refresh_token(refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="token_expired")

    from uuid import UUID
    result = await session.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="user_not_found")

    access_token = create_access_token(user.id)
    response.set_cookie("access_token", access_token, max_age=15 * 60, **_COOKIE_OPTS)
    return user


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
