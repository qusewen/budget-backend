import uvicorn
from fastapi import FastAPI, APIRouter

from pydantic import BaseModel

app = FastAPI()

router = APIRouter(prefix="", tags=["Пробный запрос"])


@router.get("/", summary="Главная ручка")
async def root():
    return {"message": "Hello World"}


@router.get("/test", summary="Главная ручка 2")
async def root():
    return {"message": "test"}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)