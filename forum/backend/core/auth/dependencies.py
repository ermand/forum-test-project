from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from core.auth.jwt import SECRET_KEY, ALGORITHM
from src.models.user import User
from core.db_connection.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token i pavlefshëm")
    except JWTError:

        raise HTTPException(status_code=401, detail="Nuk mund të vërtetohet identiteti")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Përdoruesi nuk u gjet")

    return user