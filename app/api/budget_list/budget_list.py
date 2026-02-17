from certifi import where
from fastapi import APIRouter, Depends, Request, Query, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.budget_list.budget_list_alchemy import BudgetList
from app.database.database import get_db

from app.Models.budget_list.budget_list import BudgetListResponse, BudgetListCreate
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


@router_budget_list.post("", response_model=BudgetListResponse, status_code=201)
async def create_budget(budget: BudgetListCreate,
                        request: Request,
                        response: Response,
                        db: AsyncSession = Depends(get_db)
                        ):
    user = await get_current_user(request, response, db)
    user_id = user.id

    new_budget = BudgetList(
        name=budget.name,
        description=budget.description,
        date=budget.date,
        value=budget.value,
        currency=budget.currency,
        content=budget.content,
        user_id=user_id,
        type_id=budget.type_id,
    )
    db.add(new_budget)
    await db.commit()

    await db.refresh(new_budget, attribute_names=["type"])


    return new_budget

@router_budget_list.delete("/{id}",status_code=200, summary="Удалить выбранную затрату ❌")
async def delete_currency(
        id: int,
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, response, db)
    user_id = user.id
    is_admin = await check_is_admin_role(request, response, db)

    query = select(BudgetList).where(BudgetList.id == id)
    result = await db.execute(query)
    budget = result.scalar_one_or_none()
    if is_admin == False and budget.user_id != user_id:
        raise HTTPException(status_code=400, detail="У пользователя нет данной записи")
    if budget is None:
        raise HTTPException(status_code=404, detail="Затрата не найдена")
    await db.delete(budget)
    await db.commit()

    return {"message": "Затрата удалена"}