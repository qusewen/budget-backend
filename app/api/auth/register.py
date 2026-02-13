import asyncpg
from fastapi import APIRouter, Depends, Request, Response

from app.database.database import get_db_connection
from app.helpers.auth.hashed_password import hash_password, verify_password
from app.Models.auth.auth_models import (RegisterResponse,
                                         ResetPasswordResponse, ResetResponse,
                                         UserCreate, LoginResponse)
from app.helpers.auth.remove_cookie import remove_cookie
from app.helpers.auth.set_cookie import set_cookie
from app.helpers.auth.token import decode_access_token, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Регистрация 🪪"])


@router.post("/register", response_model=RegisterResponse, status_code=201, summary="регистрация нового пользователя 🤵‍♂️🤵‍♀️")
async def register(
    user: UserCreate, db: asyncpg.Connection = Depends(get_db_connection)
):
    hashed = hash_password(user.password)

    await db.execute(
        """
         INSERT INTO users(name, email, password, age)
         VALUES($1, $2, $3, $4)
    """,
        user.name,
        user.email,
        hashed,
        user.age,
    )

    newUser = await db.fetchrow("SELECT * FROM users WHERE email = $1", user.email)
    user_dict = dict(newUser)

    return {"message": "Пользователь создан!", "user": user_dict}


@router.post("/reset-password", response_model=ResetResponse, status_code=201, summary="Сброс пароля ✏️")
async def reset_password(
    pas: ResetPasswordResponse, db: asyncpg.Connection = Depends(get_db_connection)
):
    user = await db.fetchrow(
        "SELECT id, password FROM users WHERE email = $1", pas.email
    )
    if not user:
        return {"message": "Пользователь не найден"}
    else:
        dict_user = dict(user)
        hashed = hash_password(pas.new_password)
        if verify_password(pas.prev_password, dict_user["password"]):
            if verify_password(pas.new_password, dict_user["password"]):
                return {"message": "Пароль не может быть прежним"}
            else:
                await db.execute(
                    "UPDATE users SET password = $1 WHERE email = $2", hashed, pas.email
                )
                return {"message": "Пароль успешно изменен"}
        else:
            return {"message": "Старый пароль невереный"}

@router.post('/refresh_access_token', response_model=LoginResponse, status_code=201, summary="Обновление refresh токена 🕗", description="Энд поинт по которому можно обновить токен")
async def refresh_access_token(request: Request, response: Response):
    refresh_token = request.cookies.get('refresh_token')
    decode_refresh = decode_access_token(refresh_token)
    if decode_refresh is not None:
        access_token = create_access_token(decode_refresh)
        refresh_token = create_refresh_token(decode_refresh)
        await set_cookie(response, access_token, refresh_token)

        return {
            "message": "Токен успешно обновлен",
            "refresh_token": refresh_token,
            "access_token": access_token,
        }
    else:
        await remove_cookie(response)
        return {
            "message": "Ошибка обновления токена. Истек срок действия токена",
            "refresh_token": None,
            "access_token": None,
        }


