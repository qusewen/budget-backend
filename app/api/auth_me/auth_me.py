from fastapi import APIRouter, Depends

from app.helpers.auth.check_login import get_current_user
from app.Models.auth.auth_models import UserWrapper

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserWrapper)
async def auth_me(current_user=Depends(get_current_user)):
    user_dict = dict(current_user)
    return {"user": user_dict}
