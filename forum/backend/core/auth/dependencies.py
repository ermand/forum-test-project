from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from src.models.user import User
from core.db_connection.session import SessionDep
from core.auth.jwt import AccessTokenError, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")
OAuth2TokenDep = Annotated[str, Depends(oauth2_scheme)]


from sqlalchemy import select
from fastapi import HTTPException

async def get_current_user(
    token: OAuth2TokenDep,
    db: SessionDep,
) -> User:
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except AccessTokenError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]
