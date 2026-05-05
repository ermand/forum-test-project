from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pyjwt as jwt
from jwt.exceptions import InvalidTokenError

from src.config.settings import settings


class AccessTokenError(Exception):
    pass


def create_access_token(
    *,
    subject: str | None = None,
    data: dict | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    data = data.copy() if data else {}
    if subject is not None:
        data["sub"] = subject

    if "sub" not in data:
        raise ValueError("Access tokens require a subject")

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    data.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid4()),
            "typ": "access",
        }
    )

    return jwt.encode(data, settings.JWT_PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except InvalidTokenError as exc:
        raise AccessTokenError("Could not validate credentials") from exc

    if payload.get("typ") != "access" or not payload.get("sub"):
        raise AccessTokenError("Could not validate credentials")

    return payload
