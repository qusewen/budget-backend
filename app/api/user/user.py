from fastapi import APIRouter, Depends, Request, status, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.Models.auth.auth_models import CurrentUserResponse, UpdateUser
from app.Models.auth.user import User
from app.Models.role.role import Role
from app.Models.role.role_types import RoleTypeResponse
from app.database.database import get_db
from app.helpers.auth.check_login import get_current_user
from app.helpers.update.check_fields import validate_foreign_keys

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


@router_user.patch("", response_model=CurrentUserResponse, status_code=200, summary='Обновить пользователя ✏️')
async def patch_current_user(
        request: Request,
        response: Response,
        update_data: UpdateUser,
        db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(request, response, db)
    update_data_dict = update_data.model_dump(exclude_unset=True)

    if update_data_dict.get('email') is not None:
        query = select(User).where(User.email == update_data_dict.get('email'))
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user and existing_user.__dict__.get('email') != user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
    if update_data_dict.get('role_id') is not None:
        query = select(Role).where(Role.id == update_data_dict.get('role_id'))
        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой роли не существует"
            )



    await validate_foreign_keys(db, user, update_data_dict)
    for field, value in update_data_dict.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user, attribute_names=["role"])

    return user


@router_user.delete('', status_code=200, summary='Удалить аккаунт 🧨')
async def delete_current_user(
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(request, response, db)
    if user is not None:
        await db.delete(user)
        await db.commit()
        return {"message": "Пользователь удален"}
