import os

import httpx

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.currency.currency_alchemy import CurrencyAlchemy
from app.Models.currency.currency_model import CurrencyApiData
from app.database.database import get_db

load_dotenv()
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")


async def get_currency(db: AsyncSession = Depends(get_db), type_id: int | None = None):
    query = select(CurrencyAlchemy)
    cur = await db.execute(query)
    cur_res =  cur.scalars().all()

    names = [currency.short_name for currency in cur_res]
    name_result_str = ",".join(names)


    query_type=select(CurrencyAlchemy).where(CurrencyAlchemy.id == type_id)
    cur_type = await db.execute(query_type)
    cur_res_type = cur_type.scalar_one_or_none()

    type_name = cur_res_type.short_name

    url = f'https://apilayer.net/api/live?access_key={CURRENCY_API_KEY}&currencies={name_result_str}&source={type_name}&format=1'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_currency_one(db: AsyncSession = Depends(get_db), type_id: int | None = None, wallet_type_id: int | None  = None) -> CurrencyApiData:

    query=select(CurrencyAlchemy).where(CurrencyAlchemy.id == wallet_type_id)
    cur = await db.execute(query)
    cur_res = cur.scalar_one_or_none()

    names = cur_res.short_name
    print(names)
    query_type=select(CurrencyAlchemy).where(CurrencyAlchemy.id == type_id)
    cur_type = await db.execute(query_type)
    cur_res_type = cur_type.scalar_one_or_none()

    type_name = cur_res_type.short_name

    url = f'https://apilayer.net/api/live?access_key={CURRENCY_API_KEY}&currencies={names}&source={type_name}&format=1'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        data['fields'] = f'{type_name}{names}'

        currency_data = CurrencyApiData(**data)

        return currency_data