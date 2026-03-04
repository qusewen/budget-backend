import uvicorn
from fastapi import Depends, FastAPI, Response, UploadFile, File
from starlette.responses import StreamingResponse

from app.api.auth.login import router as login_router
from app.api.auth.register import router
from app.api.auth_me.auth_me import router as login_router_auth
from app.api.budget_list.budget_list import router_budget_list
from app.api.currency.currency import router_currency
from app.api.income.income import router_income_list
from app.api.wallet.walet import router_wallet
from app.s3_service import S3Service

app = FastAPI()


s3 = S3Service()

app.include_router(router)
app.include_router(login_router)
app.include_router(login_router_auth)
app.include_router(router_currency)
app.include_router(router_income_list)
app.include_router(router_budget_list)
app.include_router(router_wallet)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)