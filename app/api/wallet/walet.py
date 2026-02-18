from fastapi import APIRouter, Depends, Request, Query, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.other.meta_data import PaginatedResponse
from app.Models.wallet.wallet_model import WalletResponse, WalletCreate, WalletUpdateValue
from app.Models.wallet.wallet_model_alchemy import Wallet
from app.database.database import get_db
from app.helpers.auth.check_login import get_current_user
from app.helpers.auth.check_role import check_is_admin_role
from app.helpers.other.meta_generator import meta_generator

router_wallet = APIRouter(prefix="/wallet", tags=["Кошельки 👛"], dependencies=[Depends(get_current_user)])


@router_wallet.get("", status_code=200, response_model=PaginatedResponse[WalletResponse], summary='Получить свои кошельки 👛')
async def get_wallet(
        request: Request,
        response: Response,
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(15, ge=1, le=100, description="Элементов на странице"),
        db: AsyncSession = Depends(get_db)
):
    user = await get_current_user(request, response, db)
    user_id = user.id
    offset = (page - 1) * per_page
    is_admin = await check_is_admin_role(request, response, db)


    query = select(Wallet).options(
        selectinload(Wallet.currency)
    )

    if not is_admin:
        query = query.where(Wallet.user_id == user_id)

    query = query.order_by(Wallet.user_id).offset(offset).limit(per_page)
    pagination = await meta_generator(page, per_page, Wallet, db)
    result = await db.execute(query)
    wallets = result.scalars().all()
    wallets_list = list(wallets)

    return PaginatedResponse(
        data=wallets_list,
        meta=pagination
    )


@router_wallet.post("", status_code=201, response_model=WalletResponse, summary='Создать новый кошелек 💰')
async def create_wallet(
        new_wallet: WalletCreate,
        request: Request,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    user = await get_current_user(request, response, db)
    user_id = user.id

    prev_wallet_query = select(Wallet).where(Wallet.user_id == user_id, Wallet.currency_id == new_wallet.currency_id)
    prev_wallet = await db.execute(prev_wallet_query)
    prev_wallet_data = prev_wallet.scalar_one_or_none()

    if prev_wallet_data is not None:
        raise HTTPException(status_code=400, detail='Кошелек с похожей валютой существует')

    if new_wallet.is_general:
        query = select(Wallet).where(Wallet.user_id == user_id, Wallet.is_general == True).with_for_update()
        wallet = await db.execute(query)
        wallet_res = wallet.scalar_one_or_none()
        if wallet_res is not None:
            wallet_res.is_general = False
            db.add(wallet_res)

    wallet_dto = Wallet(
        value = new_wallet.value,
        description = new_wallet.description,
        currency_id=new_wallet.currency_id,
        is_general=new_wallet.is_general,
        user_id = user_id
    )
    db.add(wallet_dto)
    await db.commit()
    await db.refresh(wallet_dto, attribute_names=["currency"])

    return wallet_dto

#
# @router_wallet.patch("/id", response_model=WalletResponse, status_code=200, summary='Манипуляции с сумой на кошельке')
# async def update_wallet(
#         update_data: WalletUpdateValue,
#         request: Request,
#         response: Response,
#         db: AsyncSession = Depends(get_db)):
#     user = await get_current_user(request, response, db)
#     user_id = user.id
#
#
#
