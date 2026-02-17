from fastapi import APIRouter, Depends, Request, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.budget_list.budget_list_alchemy import BudgetList
from app.database.database import get_db

from app.Models.budget_list.budget_list import BudgetListResponse
from app.helpers.auth.check_login import get_current_user
from app.helpers.auth.check_role import check_is_admin_role

router_budget_list = APIRouter(prefix="/budget", tags=["Затраты 💴"], dependencies=[Depends(get_current_user)])


@router_budget_list.get("", response_model=list[BudgetListResponse], status_code=200)
async def get_currencies(
        request: Request,
        response: Response,
        page: int = Query(1, description="Номер страницы"),
        per_page: int = Query(15, description="Элементов на странице"),
        db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, response, db)
    user_id = user.id
    offset = (page - 1) * per_page
    is_admin = await check_is_admin_role(request, response, db)
    query = select(BudgetList).options(
        selectinload(BudgetList.type)
    )
    if not is_admin:
        query = query.where(BudgetList.user_id == user_id)

    query = query.order_by(BudgetList.id).offset(offset).limit(per_page)

    result = await db.execute(query)
    budgets = result.scalars().all()
    return budgets