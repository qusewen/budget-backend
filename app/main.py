import uvicorn
from fastapi import Depends, FastAPI, Response

from app.api.auth.login import router as login_router
from app.api.auth.register import router
from app.api.auth_me.auth_me import router as login_router_auth
from app.api.currency.currency import router_currency

app = FastAPI()


app.include_router(router)
app.include_router(login_router)
app.include_router(login_router_auth)
app.include_router(router_currency)



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)