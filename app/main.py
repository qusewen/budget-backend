from fastapi import FastAPI, Depends, Response

from app.helpers.auth.check_login import get_current_user
from app.api.auth.register import router
from app.api.auth.login import router as login_router
from app.api.auth_me.auth_me import router as login_router_auth

app = FastAPI()


app.include_router(router)
app.include_router(login_router)
app.include_router(login_router)
app.include_router(login_router_auth)



@app.get("/test")
async def get_test(response: Response, current_user = Depends(get_current_user)):
    return {"message": "login success"}