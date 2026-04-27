from sqlalchemy.orm import Session
from src.models.user import User
from src.schemas.user import UserCreate
from core.auth.password import hash_password, verify_password



def create_user(db: Session, user: UserCreate):
    password = hash_password(user.password)

    db_user = User(
        username = user.username,
        email = user.email,
        password_hash = password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id==user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False

    if not verify_password(password, user.password_hash):
        return False

    return user