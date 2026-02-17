from fastapi import APIRouter, Depends, Response, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db

from app.Models.auth.user import User
from app.helpers.auth.hashed_password import verify_password
from app.helpers.auth.set_cookie import set_cookie
from app.helpers.auth.token import create_access_token, create_refresh_token
from app.Models.auth.auth_models import Login, LoginResponse

router = APIRouter(prefix="/auth", tags=["Авторизация 🔓"])


@router.post("/login", response_model=LoginResponse, status_code=201, summary="Логин 🔑")
async def login(
        credential: Login,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == credential.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return LoginResponse(
            message="Неверный логин или пароль",
            refresh_token=None,
            access_token=None
        )

    if not verify_password(credential.password, user.password):
        return LoginResponse(
            message="Неверный логин или пароль",
            refresh_token=None,
            access_token=None
        )

    token_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "isactive": user.isactive
    }

    refresh_token = create_refresh_token(token_data)
    access_token = create_access_token(token_data)

    await set_cookie(response, access_token, refresh_token)

    return LoginResponse(
        message="Авторизация прошла успешно",
        refresh_token=refresh_token,
        access_token=access_token
    )


@router.post("/logout", summary="Разлогин 🔐")
async def logout(response: Response, request: Request):
    if request.cookies.get('refresh_token') is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не в системе"
        )
    if request.cookies.get('access_token') is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не в системе"
        )

    response.delete_cookie("refresh_token")
    response.delete_cookie("access_token")

    return {"message": "Пользователь разлогинен"}