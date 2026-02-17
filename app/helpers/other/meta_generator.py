from typing import Type

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.other.meta_data import PaginationMeta
from app.database.base import Base
from app.database.database import get_db


async def meta_generator(
    page: int,
    per_page: int,
    model: Type[Base],
db: AsyncSession = Depends(get_db)
):
    count_query = select(func.count()).select_from(model)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    total_pages = (total + per_page - 1) // per_page

    results = PaginationMeta(
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

    return results