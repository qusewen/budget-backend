import asyncpg
from fastapi import APIRouter, Depends

from app.database.database import get_db_connection
from app.helpers.auth.hashed_password import hash_password, verify_password
from app.Models.auth.auth_models import (RegisterResponse,
                                         ResetPasswordResponse, ResetResponse,
                                         UserCreate)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
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


@router.post("/reset-password", response_model=ResetResponse, status_code=201)
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
