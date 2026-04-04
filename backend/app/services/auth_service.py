from datetime import datetime, timedelta
from typing import Optional
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.ACCESS_SECRET, algorithm="HS256")


def create_refresh_token(user_id: uuid.UUID) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.REFRESH_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> Optional[str]:
    """Returns user_id string or None."""
    try:
        payload = jwt.decode(token, settings.ACCESS_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[str]:
    """Returns user_id string or None."""
    try:
        payload = jwt.decode(token, settings.REFRESH_SECRET, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return None
        return payload.get("sub")
    except JWTError:
        return None
