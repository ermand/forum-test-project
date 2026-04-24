from datetime import datetime, timedelta, timezone
from jose import jwt

#komanda né terminal per gjenerimin e secret key // python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = "fefefed0bce0950b0df9628fd4fd385da311584aa33d7578599c4dc342f5405a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10


def create_access_token(data: dict):
    to_encode = data.copy()


    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})


    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt