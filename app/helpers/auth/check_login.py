import asyncpg
from fastapi import Depends, HTTPException, Request, Response, status
from starlette.responses import JSONResponse

from app.database.database import get_db_connection
from app.helpers.auth.token import decode_access_token


async def get_current_user(
    request: Request,
    response: Response,
    db: asyncpg.Connection = Depends(get_db_connection),
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    decoded_access_token = decode_access_token(access_token)
    if decoded_access_token is None:
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Unauthorized"}
        )

    select_user = await db.fetchrow(
        "SELECT * FROM users WHERE email = $1", decoded_access_token.get("email")
    )

    if not select_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return select_user
