from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db_connection.session import get_db
from src.schemas.user import UserResponse
from core.auth.dependencies import get_current_user
from src.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user=Depends(get_current_user)):
    return current_user


@router.get("/{id}", response_model=UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db)):
    user = user_service.get_user_by_id(db, user_id=id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
