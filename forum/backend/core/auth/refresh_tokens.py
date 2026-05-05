from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe

from sqlalchemy.orm import Session

from src.config.settings import settings
from src.models.refresh_token import RefreshToken
from src.models.user import User


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def hash_refresh_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def create_refresh_token(db: Session, user: User) -> str:
    token = token_urlsafe(64)
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(token),
        expires_at=_utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    return token


def rotate_refresh_token(db: Session, token: str) -> tuple[User, str] | None:
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_refresh_token(token))
        .first()
    )

    if not db_token:
        return None

    if (
        db_token.revoked_at is not None
        or _as_aware_utc(db_token.expires_at) <= _utcnow()
    ):
        return None

    db_token.revoked_at = _utcnow()
    new_token = create_refresh_token(db, db_token.user)
    db_token.replaced_by_hash = hash_refresh_token(new_token)
    return db_token.user, new_token


def revoke_refresh_token(db: Session, token: str) -> bool:
    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_refresh_token(token))
        .first()
    )
    if not db_token or db_token.revoked_at is not None:
        return False

    db_token.revoked_at = _utcnow()
    return True
