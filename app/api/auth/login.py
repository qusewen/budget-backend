import asyncpg
from fastapi import APIRouter, Depends, Response, Request, HTTPException

from app.database.database import get_db_connection
from app.helpers.auth.hashed_password import verify_password
from app.helpers.auth.set_cookie import set_cookie
from app.helpers.auth.token import create_access_token, create_refresh_token
from app.Models.auth.auth_models import Login, LoginResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["Авторизация 🔓"])


@router.post("/login", response_model=LoginResponse, status_code=201, summary="Логин 🔑")
async def login(
    credential: Login,
    response: Response,
    db: asyncpg.Connection = Depends(get_db_connection),
):

    user: UserCreate = await db.fetchrow(
        "SELECT * FROM users WHERE email = $1", credential.email
    )
    user_dict = dict(user)
    if user is not None:
        if verify_password(credential.password, user_dict["password"]):
            user_dict.pop("password")

            refresh_token = create_refresh_token(user_dict)
            access_token = create_access_token(user_dict)
            await set_cookie(response, access_token, refresh_token)
            return {
                "message": "Авторизация прошла успешно",
                "refresh_token": refresh_token,
                "access_token": access_token,
            }
        else:
            return {"message": "Не верный логин или пароль"}
    else:
        return {"message": "Пользователь не найден"}


@router.post("/logout", summary="Разлогин 🔐")
async def logout(response: Response, request: Request):

    if request.cookies.get('refresh_token') is None:
        raise HTTPException(status_code=401, detail="Пользователь не в системе")
    if request.cookies.get('access_token') is None:
        raise HTTPException(status_code=401, detail="Пользователь не в системе")

    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")
    return {"message": "Пользователь разлогинен"}
