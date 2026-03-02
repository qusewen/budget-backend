from fastapi import APIRouter, Depends, Request, Query, Response, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.budget_list.budget_list_alchemy import BudgetList
from app.Models.expense_type.expense_type import ExpenseType

from app.Models.other.enums import SortDirection
from app.Models.other.meta_data import PaginatedResponse
from app.Models.wallet.wallet_model_alchemy import Wallet
from app.database.database import get_db

from app.Models.budget_list.budget_list import BudgetListResponse, BudgetListCreate, BudgetListUpdate, SortField
from app.helpers.auth.check_login import get_current_user
from app.helpers.auth.check_role import check_is_admin_role
from app.helpers.other.get_currency import get_currency, get_currency_one
from app.helpers.other.meta_generator import meta_generator
from app.helpers.update.check_fields import validate_foreign_keys

router_budget_list = APIRouter(prefix="/budget", tags=["Затраты 💴"], dependencies=[Depends(get_current_user)])


@router_budget_list.get("", response_model=PaginatedResponse[BudgetListResponse], status_code=200,
                        summary="Получить все затраты 💵")
async def get_currencies(
        request: Request,
        response: Response,
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(15, ge=1, le=100, description="Элементов на странице"),
        sort_by: SortField = Query(SortField.ID, description="Поле для сортировки"),
        sort_direction: SortDirection = Query(SortDirection.ASC, description="Направление сортировки"),
        db: AsyncSession = Depends(get_db)):
    user = await get_current_user(request, response, db)
    user_id = user.id
    offset = (page - 1) * per_page
    is_admin = await check_is_admin_role(request, response, db)

    sort_column = getattr(BudgetList, sort_by.value)
    if sort_direction == SortDirection.ASC:
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()

    query = select(BudgetList).options(
        selectinload(BudgetList.type)
    )

    if not is_admin:
        query = query.where(BudgetList.user_id == user_id)

    query = query.order_by(sort_column).offset(offset).limit(per_page)
    pagination = await meta_generator(page, per_page, BudgetList, db)
    result = await db.execute(query)
    budgets = result.scalars().all()
    budgets_list = list(budgets)

    return PaginatedResponse(
        data=budgets_list,
        meta=pagination
    )


@router_budget_list.post("", response_model=BudgetListResponse, status_code=201, summary="Добавить новую затрату 💶")
async def create_budget(budget: BudgetListCreate,
                        request: Request,
                        response: Response,
                        db: AsyncSession = Depends(get_db)
                        ):
    user = await get_current_user(request, response, db)
    user_id = user.id

    wallet = select(Wallet).where(Wallet.user_id == user_id, Wallet.id == budget.wallet_id).with_for_update()
    wallet_result = await db.execute(wallet)
    wallet_res = wallet_result.scalar_one_or_none()


    types_query = select(ExpenseType).where(ExpenseType.id == budget.type_id)
    types_result = await db.execute(types_query)
    types = types_result.scalar_one_or_none()


    if wallet_res is None:
        raise HTTPException(status_code=400, detail="Данного кошелька не существует")

    if types is None:
        raise HTTPException(status_code=400, detail="Данного типа затрат не существует")

    result_cur_data = await get_currency_one(db, budget.currency, wallet_res.currency_id)
    new_budget = budget.value * result_cur_data.quotes[result_cur_data.fields]

    if wallet_res.value < new_budget:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    print(result_cur_data)


    wallet_res.value -= new_budget
    db.add(wallet_res)
    new_budget = BudgetList(
        name=budget.name,
        description=budget.description,
        date=budget.date,
        value=budget.value,
        currency=budget.currency,
        content=budget.content,
        user_id=user_id,
        type_id=budget.type_id,
        currency_value= result_cur_data.quotes[result_cur_data.fields],
        wallet_id = wallet_res.id,
        type_budget = 'expense'
    )
    db.add(new_budget)
    await db.commit()

    await db.refresh(new_budget, attribute_names=["type"])

    return new_budget


@router_budget_list.patch("/{id}", response_model=BudgetListResponse, status_code=200,
                          summary='Обновить выбранную затрату ✏️')
async def update_budget(
        id: int,
        update_data: BudgetListUpdate,
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db)):

    query = select(BudgetList).where(BudgetList.id == id)
    result = await db.execute(query)
    budget = result.scalar_one_or_none()
    user = await get_current_user(request, response, db)
    user_id = user.id
    is_admin = await check_is_admin_role(request, response, db)

    if not budget:
        raise HTTPException(status_code=404, detail=f"Затрата с id {id} не найдена")

    update_data_dict = update_data.model_dump(exclude_unset=True)

    if not is_admin and budget.user_id != user_id:
        raise HTTPException(status_code=403,
                            detail="У пользователя нет прав на редактирование данной записи")

    if not update_data_dict:
        raise HTTPException(status_code=400, detail="Нет полей для обновления")


    await validate_foreign_keys(db, budget, update_data_dict)


    for field, value in update_data_dict.items():
        setattr(budget, field, value)

    await db.commit()
    await db.refresh(budget, attribute_names=["type"])

    return budget


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

    wallet = select(Wallet).where(Wallet.user_id == user_id, Wallet.id == budget.wallet_id).with_for_update()
    wallet_result = await db.execute(wallet)
    wallet_res = wallet_result.scalar_one_or_none()

    new_budget = budget.value * budget.currency_value

    wallet_res.value += new_budget
    db.add(wallet_res)

    await db.delete(budget)
    await db.commit()

    return {"message": "Затрата удалена"}