from sqlalchemy.orm import Session
from src.models.posts import Post
from src.schemas.posts import PostCreate, PostUpdate


def create_new_post(db: Session, post_data: PostCreate, user_id: int):
    db_post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Post).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()


def update_post(db: Session, post_id: int, post_update: PostUpdate, user_id: int):
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if not db_post:
        return None

    if db_post.user_id != user_id:
        return "forbidden"

    if post_update.title:
        db_post.title = post_update.title
    if post_update.content:
        db_post.content = post_update.content

    db.commit()
    db.refresh(db_post)
    return db_post


def delete_posts(db: Session, id: int, user_id: int):
    db_post = db.query(Post).filter(Post.id == id).first()
    if not db_post:
        return None

    if db_post.user_id != user_id:
        return "forbidden"

    db.delete(db_post)
    db.commit()

    return True
