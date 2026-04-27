from datetime import datetime, timedelta, timezone
from jose import jwt
from src.config.settings import Settings


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
    return encoded_jwt