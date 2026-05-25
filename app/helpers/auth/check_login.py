from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.Models.auth.user import User
from app.database.database import get_db
from app.helpers.auth.remove_cookie import remove_cookie
from app.helpers.auth.token import decode_access_token


async def get_current_user(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нет активных пользователей, авторизируйтесь в приложении"
        )

    decoded_access_token = decode_access_token(access_token)
    if decoded_access_token is None:
        await remove_cookie(response)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Пользователь не в системе"}
        )

    query = select(User).where(User.email == decoded_access_token.get("email"))
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нет активных пользователей, авторизируйтесь в приложении"
        )

        # ДЛЯ ОТЛАДКИ: вывод всех данных пользователя
    print("=== USER DATA ===")
    print(f"User type: {type(user)}")

    # Если user - это объект SQLAlchemy
    if hasattr(user, "__dict__"):
        # Исключаем служебные атрибуты SQLAlchemy
        user_dict = {k: v for k, v in user.__dict__.items() if not k.startswith('_')}
        print("User dict:", user_dict)

    # Вывод конкретных атрибутов
    print(f"User ID: {getattr(user, 'id', 'Not found')}")
    print(f"User email: {getattr(user, 'email', 'Not found')}")
    print(f"User username: {getattr(user, 'username', 'Not found')}")
    print("================")
    return user
