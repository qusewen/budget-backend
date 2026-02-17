import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", '1')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", '1')

from fastapi import Response
async def set_cookie(
    response: Response,
    access_token: str = None,
    refresh_token: str = None,
):
    max_age_refresh = int(timedelta(minutes=float(REFRESH_TOKEN_EXPIRE_DAYS)).total_seconds())
    max_age_access = int(timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)).total_seconds())

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=max_age_refresh,
        expires=max_age_refresh,
        samesite="lax",
        secure=True,
        path="/refresh_access_token",
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=max_age_access,
        expires=max_age_access,
        samesite="lax",
        secure=True,
        path="/",
    )
    return True