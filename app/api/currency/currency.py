import asyncpg
from fastapi import APIRouter, Depends, Request, Query, HTTPException

from app.Models.currency.currency_model import CurrencyRequest, CurrencyResponse, SortField, CurrencyUpdate
from app.Models.other.enums import SortDirection
from app.database.database import get_db_connection
from app.helpers.auth.check_login import get_current_user

router_currency = APIRouter(prefix="/currency", tags=["Валюта 💴"], dependencies=[Depends(get_current_user)])


@router_currency.get("", response_model=list[CurrencyResponse], status_code=200, summary='Получить список валют 💸')
async def get_currencies(
    page: int = Query(1, description="Номер страницы"),
    per_page: int = Query(15, description="Элементов на странице"),
    sort_by: SortField = Query(SortField.ID, description="Поле для сортировки"),
    sort_direction: SortDirection = Query(SortDirection.ASC, description="Направление сортировки"),
    db: asyncpg.Connection = Depends(get_db_connection)):
    offset = (page - 1) * per_page
    query = f"""
        SELECT * FROM currency 
        ORDER BY {sort_by.value} {sort_direction.value} 
        LIMIT $1 OFFSET $2
    """

    rows = await db.fetch(query, per_page, offset)
    return [CurrencyResponse(**dict(row)) for row in rows]



@router_currency.get("/{id}", response_model=CurrencyResponse, status_code=200, summary='Получить выбранную валюту 💸')
async def get_currencies(id: int, db: asyncpg.Connection = Depends(get_db_connection)):
    row = await db.fetchrow("SELECT * FROM currency WHERE id = $1", id)
    if row is None:
        raise HTTPException(status_code=404, detail="Данная валюта не найдена")
    return CurrencyResponse(**dict(row))


@router_currency.post("", response_model=CurrencyResponse, status_code=201, summary='Добавить новую валюту 💶')
async def create_new_currency(currency: CurrencyRequest, db: asyncpg.Connection = Depends(get_db_connection)):
    if id is None:
        raise HTTPException(status_code=400, detail="Вы не передали id")
    prev_currency = await db.fetchrow("SELECT * FROM currency WHERE name = $1", currency.name)
    if prev_currency is not None:
        raise HTTPException(status_code=400, detail="Данная валюта уже существует, обновите существующую, либо удалите ее")
    await db.execute("INSERT INTO currency (name, value, short_name) VALUES ($1,$2, $3)", currency.name, currency.value, currency.short_name)
    new_currency = await db.fetchrow("SELECT * FROM currency WHERE name = $1", currency.name)
    return CurrencyResponse(**dict(new_currency))

@router_currency.patch("/{id}", response_model=CurrencyResponse, status_code=200, summary='Обновить выбранную валюту 🔄')
async def update_currency(id: int, update_data:CurrencyUpdate,  db: asyncpg.Connection = Depends(get_db_connection)):
    if id is None:
        raise HTTPException(status_code=400, detail="Вы не передали id")
    existing = await db.fetchrow("SELECT * FROM currency WHERE id = $1", id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Валюта с id {id} не найдена")

    update_fields = []
    values = []
    param_index = 2

    update_data_dict = update_data.model_dump(exclude_unset=True)

    if not update_data_dict:
        raise HTTPException(status_code=400, detail="Нет полей для обновления")

    for field, value in update_data_dict.items():
        update_fields.append(f"{field} = ${param_index}")
        values.append(value)
        param_index += 1

    query = f"""
        UPDATE currency 
        SET {', '.join(update_fields)}
        WHERE id = $1
        RETURNING *
    """

    updated = await db.fetchrow(query, id, *values)

    return CurrencyResponse(**dict(updated))




@router_currency.delete("/{id}", status_code=200, summary="Удалить выбранную валюту ❌")
async def delete_currency(id: int, db: asyncpg.Connection = Depends(get_db_connection)):
    if id is None:
        raise HTTPException(status_code=400, detail="Вы не передали id")
    cur = await db.fetchrow("SELECT * FROM currency WHERE id = $1", id)
    if cur is None:
        raise HTTPException(status_code=404, detail="Данная валюта не найдена")
    await db.execute("DELETE FROM currency WHERE id = $1", id)
    return {"message": 'Валюта удалена'}