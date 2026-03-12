from fastapi import APIRouter, Depends, Request, Query, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.Models.auth.auth_models import CurrentUserResponse
from app.Models.role.role import Role
from app.Models.role.role_types import RoleTypeResponse
from app.database.database import get_db
from app.helpers.auth.check_login import get_current_user

router_user = APIRouter(prefix="/user", tags=["Пользователь 🕺"], dependencies=[Depends(get_current_user)])


@router_user.get("", response_model=CurrentUserResponse, summary='Получить данный пользователя 🌐', status_code=200)
async def get_current_user_for_app(
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    user = await get_current_user(request, response, db)
    role_query = select(Role).where(Role.id == user.role_id)
    role_res = await db.execute(role_query)
    role: RoleTypeResponse | None = role_res.scalar_one_or_none()
    res_data = CurrentUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=role,
        isactive=user.isactive,
        content=user.content,
        age=user.age,
    )

    return res_data
