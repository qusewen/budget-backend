import json
import asyncpg
from fastapi import APIRouter, Depends, Request, Query, HTTPException, Response

from app.Models.budget_list import BudgetListResponse
from app.database.database import get_db_connection
from app.helpers.auth.check_login import get_current_user
from app.helpers.auth.check_role import check_is_admin_role

router_budget_list = APIRouter(prefix="/budget", tags=["Затраты 💴"], dependencies=[Depends(get_current_user)])


@router_budget_list.get("", response_model=list[BudgetListResponse], status_code=200)
async def get_currencies(
        request: Request,
        response: Response,
        page: int = Query(1, description="Номер страницы"),
        per_page: int = Query(15, description="Элементов на странице"),
        db: asyncpg.Connection = Depends(get_db_connection)):
    offset = (page - 1) * per_page
    user = await get_current_user(request, response, db)
    user_id = user['id']

    query = """
        SELECT 
            bl.id, bl.date, bl.name, bl.value, bl.currency, 
            bl.description, bl.content,
            jsonb_build_object(
                'id', bt.id,
                'name', bt.name,
                'description', bt.description,
                'content', bt.content
            ) as type
        FROM budget_list bl
        LEFT JOIN expense_types bt ON bl.type_id = bt.id
        WHERE ($4 = true OR bl.user_id = $1)
        ORDER BY bl.id
        LIMIT $2 OFFSET $3
    """

    is_admin = await check_is_admin_role(request, response, db)
    result = []

    rows = await db.fetch(query, user_id, per_page, offset, is_admin)


    for row in rows:
        row_dict = dict(row)

        if isinstance(row_dict.get('type'), str):
            row_dict['type'] = json.loads(row_dict['type'])

        result.append(BudgetListResponse(**row_dict))

    return result