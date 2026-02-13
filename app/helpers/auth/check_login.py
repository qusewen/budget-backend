import asyncpg
from fastapi import Depends, HTTPException, Request, Response, status
from starlette.responses import JSONResponse

from app.database.database import get_db_connection
from app.helpers.auth.remove_cookie import remove_cookie
from app.helpers.auth.token import decode_access_token


async def get_current_user(
    request: Request,
    response: Response,
    db: asyncpg.Connection = Depends(get_db_connection),
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Нет активных пользователей, авторизируйтесь в приложении")

    decoded_access_token = decode_access_token(access_token)
    if decoded_access_token is None:
        await remove_cookie(response)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Пользователь не в системе"}

        )

    select_user = await db.fetchrow(
        "SELECT * FROM users WHERE email = $1", decoded_access_token.get("email")
    )

    if not select_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail= "Нет активных пользователей, авторизируйтесь в приложении")

    return select_user
