from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.config.settings import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    }
    if settings.DATABASE_URL.startswith("sqlite")
    else {},
    echo=settings.DEBUG,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass
