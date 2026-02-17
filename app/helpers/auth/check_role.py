import asyncpg
from fastapi import Depends, Request, Response

from app.database.database import get_db_connection
from app.helpers.auth.check_login import get_current_user


async def check_is_admin_role(
    request: Request,
    response: Response,
    db: asyncpg.Connection = Depends(get_db_connection)):
    user = await get_current_user(request, response, db)
    role = user['role_id']
    query_user = """
    SELECT role FROM role
    WHERE id = $1
    """
    rows_user = await db.fetch(query_user, role)

    is_admin: bool = False
    for user_role in rows_user:
        row_dict = dict(user_role)
        is_admin = row_dict['role'] == 'ADMIN'

    return is_admin
