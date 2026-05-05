from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, func, select

from src.utils.schemas import PaginatedResponse, PaginationMeta, PaginationParams

T = TypeVar("T")


async def paginate(
        db: AsyncSession,
        statement: Select,
        params: PaginationParams,
) -> PaginatedResponse[T]:
    count_statement = select(func.count()).select_from(
        statement.order_by(None).subquery()
    )

    total_items = await db.scalar(count_statement) or 0

    result = await db.execute(
        statement.offset(params.offset).limit(params.limit)
    )

    items = result.scalars().all()

    return PaginatedResponse[T](
        items=list(items),
        meta=PaginationMeta(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
        ),
    )


async def paginate_sequence(
        items: Sequence[T],
        params: PaginationParams,
) -> PaginatedResponse[T]:
    start = params.offset
    end = start + params.limit

    return PaginatedResponse[T](
        items=list(items[start:end]),
        meta=PaginationMeta(
            page=params.page,
            page_size=params.page_size,
            total_items=len(items),
        ),
    )
