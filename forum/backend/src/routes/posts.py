from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.schemas.posts import PostCreate, PostResponse, PostUpdate
from src.services import post_service
from core.db_connection.session import get_db
from core.auth.dependencies import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostResponse])
def read_posts(db: Session = Depends(get_db)):
    return post_service.get_posts(db)


@router.get("/{id}", response_model=PostResponse)
def read_single_post(id: int, db: Session = Depends(get_db)):
    post = post_service.get_post(db, id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Postimi nuk u gjet"
        )
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return post_service.create_new_post(db, post_data=post, user_id=current_user.id)


@router.put("/{id}", response_model=PostResponse)
def update_post(id: int, post_update: PostUpdate, db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    updated_post = post_service.update_post(db, id, post_update, current_user.id)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if updated_post == "forbidden":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to edit this post"
        )

    return updated_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    result = post_service.delete_posts(db, id, current_user.id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if result == "forbidden":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this post"
        )

    return None
