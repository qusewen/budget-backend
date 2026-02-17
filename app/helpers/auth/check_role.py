from fastapi import Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.role.role import Role
from app.database.database import get_db
from app.helpers.auth.check_login import get_current_user


async def check_is_admin_role(
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, response, db)

    query = select(Role).where(Role.id == user.role_id)
    result = await db.execute(query)
    role = result.scalar_one_or_none()

    return role.role == 'ADMIN' if role else False
