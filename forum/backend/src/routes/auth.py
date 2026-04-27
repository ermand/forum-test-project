from fastapi import APIRouter, Depends, HTTPException, status
from core.auth.password import verify_password
from sqlalchemy.orm import Session
from src.schemas.user import  Token
from core.auth.jwt import create_access_token
from core.db_connection.session import get_db
from src.schemas.user import UserCreate, UserResponse
from src.services import user_service
from src.schemas.user import UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    existing_username = user_service.get_user_by_username(db, username=user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    new_user = user_service.create_user(db=db, user=user_data)
    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    user = user_service.get_user_by_username(db, username=user_data.username)

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(data={"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }