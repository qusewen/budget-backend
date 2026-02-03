from fastapi import APIRouter, Depends, Response

from app.database.database import get_db_connection

from app.Models.auth.auth_models import LoginResponse, Login, UserCreate

import asyncpg

from app.helpers.auth.hashed_password import hash_password, verify_password
from app.helpers.auth.token import create_refresh_token, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse, status_code = 201)
async def login(credential: Login, response: Response, db: asyncpg.Connection = Depends(get_db_connection)):

    user: UserCreate = await db.fetchrow('SELECT * FROM users WHERE email = $1', credential.email)
    user_dict = dict(user)
    if user is not None:
        if verify_password(credential.password, user_dict["password"]):
            user_dict.pop("password")

            refresh_token = create_refresh_token(user_dict)
            access_token = create_access_token(user_dict)
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                max_age=30 * 24 * 60 * 60,
                expires=30 * 24 * 60 * 60,
                samesite="lax",
                secure=True,
                path='/'
            )

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                max_age=30 * 24 * 60 * 60,
                expires=30 * 24 * 60 * 60,
                samesite="lax",
                secure=True,
                path='/'
            )
            return {"message": "Авторизация прошла успешно", "refresh_token": refresh_token, "access_token": access_token}
        else:
            return {"message": "Не верный логин или пароль"}
    else:
        return {"message": "Пользователь не найден"}


@router.post("/logout")
async def logout(response: Response):
     response.delete_cookie("refresh_token")
     response.delete_cookie("access_token")
     return {"message": 'Пользователь разлогинен'}

