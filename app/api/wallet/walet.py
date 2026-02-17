from fastapi import APIRouter, Depends, Request, Query, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.Models.other.meta_data import PaginatedResponse
from app.Models.wallet.wallet_model import WalletResponse
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

