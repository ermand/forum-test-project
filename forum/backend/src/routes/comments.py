from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from starlette import status

from src.models import User
from src.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from src.services import comment_service, post_service
from core.db_connection.session import get_db
from core.auth.dependencies import get_current_user

from src.schemas.comment import CommentCreate

router = APIRouter(tags=["Comments"])


@router.post("/posts/{id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(id: int, comment: CommentCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    comment.post_id = id
    new_comment = comment_service.comment_create(db, comment_data=comment, user_id=current_user.id)

    if not new_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return new_comment


@router.get("/posts/{id}/comments", response_model=List[CommentResponse])
def read_comments(id: int, db: Session = Depends(get_db)):
    return comment_service.get_post_comments(db, post_id=id)


@router.put("/comments/{id}", response_model=CommentResponse)
def update_comment(id: int, comment: CommentUpdate, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    comment = comment_service.update_post_comment(db, comment_data=comment, comment_id=id, user_id=current_user.id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, )
    if comment == "forbidden":
        raise HTTPException(status_code=403, detail="Not authorized")
    return comment


@router.delete("/comments/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    comment = comment_service.delete_post_comment(db, comment_id=id, user_id=current_user.id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment == "forbidden":
        raise HTTPException(status_code=403, detail="Not authorized")

    return True
