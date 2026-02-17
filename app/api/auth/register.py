from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast

from app.Models.auth.user import User
from app.Models.role.role import Role
from app.database.database import get_db
from app.helpers.auth.hashed_password import hash_password, verify_password
from app.Models.auth.auth_models import (
    RegisterResponse,
    ResetPasswordResponse,
    ResetResponse,
    UserCreate,
    LoginResponse
)
from app.helpers.auth.remove_cookie import remove_cookie
from app.helpers.auth.set_cookie import set_cookie
from app.helpers.auth.token import decode_access_token, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Регистрация 🪪"])


@router.post("/register", response_model=RegisterResponse, status_code=201,
             summary="регистрация нового пользователя 🤵‍♂️🤵‍♀️")
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    hashed_password = hash_password(user.password)
    role_enum = ENUM('USER', 'ADMIN', name='role_enum', create_type=False)

    role_query = select(Role).where(Role.role == cast("USER", role_enum))
    role_result = await db.execute(role_query)
    default_role = role_result.scalar_one()

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        age=user.age,
        isactive=True,
        role_id = default_role.id
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "message": "Пользователь создан!",
        "user": new_user
    }


@router.post("/reset-password", response_model=ResetResponse, status_code=201, summary="Сброс пароля ✏️")
async def reset_password(
        pas: ResetPasswordResponse,
        db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == pas.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "Пользователь не найден"}

    if not verify_password(pas.prev_password, user.password):
        return {"message": "Старый пароль неверный"}

    if verify_password(pas.new_password, user.password):
        return {"message": "Пароль не может быть прежним"}

    hashed_password = hash_password(pas.new_password)
    user.password = hashed_password

    await db.commit()

    return {"message": "Пароль успешно изменен"}


@router.post('/refresh_access_token', response_model=LoginResponse, status_code=201,
             summary="Обновление refresh токена 🕗")
async def refresh_access_token(
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        await remove_cookie(response)
        return LoginResponse(
            message="Refresh токен отсутствует",
            refresh_token=None,
            access_token=None
        )

    decoded_token = decode_access_token(refresh_token)

    if decoded_token is None:
        await remove_cookie(response)
        return LoginResponse(
            message="Ошибка обновления токена. Истек срок действия токена",
            refresh_token=None,
            access_token=None
        )

    email = decoded_token.get("email")
    if email:
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            await remove_cookie(response)
            return LoginResponse(
                message="Пользователь не найден",
                refresh_token=None,
                access_token=None
            )

    new_access_token = create_access_token(decoded_token)
    new_refresh_token = create_refresh_token(decoded_token)

    await set_cookie(response, new_access_token, new_refresh_token)

    return LoginResponse(
        message="Токен успешно обновлен",
        refresh_token=new_refresh_token,
        access_token=new_access_token
    )