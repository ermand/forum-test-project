from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, String, Uuid, func, literal
from sqlalchemy.orm import Mapped, mapped_column, query_expression, relationship
from core.db_connection.database import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                                          nullable=False)
    comments_count: Mapped[int] = query_expression(default_expr=literal(0))

    owner: Mapped["User"] = relationship("User", back_populates="posts", lazy="selectin")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
        lazy="raise",
        passive_deletes=True,
        order_by="Comment.created_at",
    )
