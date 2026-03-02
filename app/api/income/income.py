from fastapi import APIRouter, Depends, Request, Query, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.budget_list.budget_list_alchemy import BudgetList
from app.Models.expense_type.expense_type import ExpenseType
from app.Models.income_types.income_types import IncomeType

from app.Models.other.enums import SortDirection
from app.Models.other.meta_data import PaginatedResponse
from app.Models.wallet.wallet_model_alchemy import Wallet
from app.database.database import get_db

from app.Models.budget_list.budget_list import SortField, BudgetListResponse, BudgetListCreate, BudgetTypeResponse, \
    BudgetListUpdate
from app.helpers.auth.check_login import get_current_user
from app.helpers.auth.check_role import check_is_admin_role
from app.helpers.other.get_currency import get_currency_one
from app.helpers.other.meta_generator import meta_generator
from app.helpers.update.check_fields import validate_foreign_keys

router_income_list = APIRouter(prefix="/income", tags=["Доходы 💴"], dependencies=[Depends(get_current_user)])


@router_income_list.get(
    '',
    response_model=PaginatedResponse[BudgetListResponse],
    status_code=200,
    summary='Получить все доходы'
)
async def income_list(
        request: Request,
        response: Response,
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(15, ge=1, le=100, description="Элементов на странице"),
        sort_by: SortField = Query(SortField.ID, description="Поле для сортировки"),
        sort_direction: SortDirection = Query(SortDirection.ASC, description="Направление сортировки"),
        db: AsyncSession = Depends(get_db)
):
    user = await get_current_user(request, response, db)
    user_id = user.id
    offset = (page - 1) * per_page
    is_admin = await check_is_admin_role(request, response, db)

    sort_column = getattr(BudgetList, sort_by.value)
    if sort_direction == SortDirection.ASC:
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()

    query = select(BudgetList)

    if not is_admin:
        query = query.where(BudgetList.user_id == user_id, BudgetList.type_budget == 'income')

    query = query.order_by(sort_column).offset(offset).limit(per_page)
    pagination = await meta_generator(page, per_page, BudgetList, db)
    result = await db.execute(query)
    budgets = result.scalars().all()

    type_ids = [b.type_id for b in budgets if b.type_id]
    income_map = {}
    expense_map = {}

    if type_ids:
        income_types = await db.execute(
            select(IncomeType).where(IncomeType.id.in_(type_ids))
        )
        income_map = {it.id: it for it in income_types.scalars().all()}

        expense_types = await db.execute(
            select(ExpenseType).where(ExpenseType.id.in_(type_ids))
        )
        expense_map = {et.id: et for et in expense_types.scalars().all()}

    budgets_list = []
    for budget in budgets:
        type_data = None
        if budget.type_id:
            if budget.type_budget == 'income' and budget.type_id in income_map:
                inc = income_map[budget.type_id]
                type_data = BudgetTypeResponse(
                    id=inc.id,
                    name=inc.name,
                    description=inc.description or '',
                    content=inc.content
                )
            elif budget.type_budget == 'expense' and budget.type_id in expense_map:
                exp = expense_map[budget.type_id]
                type_data = BudgetTypeResponse(
                    id=exp.id,
                    name=exp.name,
                    description=exp.description or '',
                    content=exp.content
                )

        budgets_list.append(BudgetListResponse(
            id=budget.id,
            date=budget.date,
            name=budget.name,
            value=budget.value,
            currency=budget.currency,
            description=budget.description,
            content=budget.content,
            type=type_data,
            currency_value=budget.currency_value,
            wallet_id=budget.wallet_id,
            type_budget=budget.type_budget
        ))

    return PaginatedResponse(
        data=budgets_list,
        meta=pagination
    )


@router_income_list.post("", response_model=BudgetListResponse, status_code=201, summary="Добавить доход 💶")
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


    types_query = select(IncomeType).where(IncomeType.id == budget.type_id)
    types_result = await db.execute(types_query)
    types = types_result.scalar_one_or_none()


    if wallet_res is None:
        raise HTTPException(status_code=400, detail="Данного кошелька не существует")

    if types is None:
        raise HTTPException(status_code=400, detail="Данного типа дохода не существует")

    result_cur_data = await get_currency_one(db, budget.currency, wallet_res.currency_id)
    new_budget = budget.value * result_cur_data.quotes[result_cur_data.fields]

    wallet_res.value += new_budget
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
        type_budget = 'income'
    )
    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget, attribute_names=["type"])

    return new_budget

@router_income_list.post("", response_model=BudgetListResponse, status_code=201, summary="Добавить доход 💶")
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


    types_query = select(IncomeType).where(IncomeType.id == budget.type_id)
    types_result = await db.execute(types_query)
    types = types_result.scalar_one_or_none()


    if wallet_res is None:
        raise HTTPException(status_code=400, detail="Данного кошелька не существует")

    if types is None:
        raise HTTPException(status_code=400, detail="Данного типа дохода не существует")

    result_cur_data = await get_currency_one(db, budget.currency, wallet_res.currency_id)
    new_budget = budget.value * result_cur_data.quotes[result_cur_data.fields]



    wallet_res.value += new_budget
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
        type_budget = 'income'
    )
    db.add(new_budget)
    await db.commit()

    await db.refresh(new_budget, attribute_names=["type"])

    return new_budget


@router_income_list.patch("/{id}", response_model=BudgetListResponse, status_code=200,
                          summary='Обновить выбранный доход ✏️')
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
        raise HTTPException(status_code=404, detail=f"Доход с id {id} не найдена")

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


@router_income_list.delete("/{id}",status_code=200, summary="Удалить выбранный доход ❌")
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
        raise HTTPException(status_code=404, detail="Доход не найден")

    wallet = select(Wallet).where(Wallet.user_id == user_id, Wallet.id == budget.wallet_id).with_for_update()
    wallet_result = await db.execute(wallet)
    wallet_res = wallet_result.scalar_one_or_none()

    new_budget = budget.value * budget.currency_value

    wallet_res.value -= new_budget
    db.add(wallet_res)

    await db.delete(budget)
    await db.commit()

    return {"message": "Доход удален"}