from sqlalchemy.orm import Session
from src.models import Post, Comment, User

from src.schemas.comment import CommentCreate, CommentUpdate


def comment_create(db: Session, comment_data: CommentCreate, user_id: int):
    post = db.query(Post).filter(Post.id == comment_data.post_id).first()
    if not post:
        return None

    new_comment = Comment(
        content=comment_data.content,
        user_id=user_id,
        post_id=comment_data.post_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def get_post_comments(db: Session, post_id: int):
    return db.query(Comment).filter(Comment.post_id == post_id).all()


def update_post_comment(db: Session, comment_id: int, comment_data: CommentUpdate, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        return None

    if comment.user_id != user_id:
        return "forbidden"

    if comment_data.content:
        comment.content = comment_data.content

    db.commit()
    db.refresh(comment)
    return comment


def delete_post_comment(db: Session, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        return None
    if comment.user_id != user_id:
        return "forbidden"

    db.delete(comment)
    db.commit()
    return True