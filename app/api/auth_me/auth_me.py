from fastapi import APIRouter, Depends

from app.helpers.auth.check_login import get_current_user
from app.Models.auth.auth_models import UserWrapper

router = APIRouter(prefix="/auth", tags=["Авторизация 🔓"])


@router.get("/me", response_model=UserWrapper, summary="Получить данные пользователя в системе 🙍‍♂️")
async def auth_me(current_user=Depends(get_current_user)):
    return {"user": current_user}
