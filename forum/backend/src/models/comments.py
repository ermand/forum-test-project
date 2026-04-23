from sqlalchemy import  Integer, Column, String, DateTime, ForeignKey , func
from sqlalchemy.orm import relationship
from core.db_connection.database import Base

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")