from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from enum import Enum

class CurrencyRequest(BaseModel):
    name: str = Field(...)
    short_name: str = Field(...)
    value: float = Field(...)

    @model_validator(mode='before')
    def check_fields_presence(cls, values):
        required_fields = ['name', 'short_name', 'value']

        if not isinstance(values, dict):
            return values

        missing_fields = []
        for field in required_fields:
            if field not in values or values[field] is None:
                missing_fields.append(field)

        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
            )
        return values

    @field_validator('short_name')
    def validate_short_name(cls, v: str) -> str:

        if len(v) > 3:
            raise HTTPException(
                status_code=400,
                detail=f"Максимальная длина короткого названия валюты 3 символа, получено {len(v)}"
            )
        if len(v) < 1:
            raise HTTPException(
                status_code=400,
                detail=f"Короткое название не может быть пустым"
            )
        return v.upper()

    @field_validator('name')
    def validate_name(cls, v: str) -> str:
        if len(v) < 2:
            raise HTTPException(
                status_code=400,
                detail=f"Минимальная длина названия валюты 2 символа, получено {len(v)}"
            )
        if len(v) > 50:
            raise HTTPException(
                status_code=400,
                detail=f"Максимальная длина названия валюты 50 символов, получено {len(v)}"
            )
        return v.strip()

    @field_validator('value')
    def validate_value(cls, v: float) -> float:
        if v < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Значение должно быть больше 0, получено {v}"
            )
        if v > 1_000_000:
            raise HTTPException(
                status_code=400,
                detail=f"Значение слишком большое. Максимум 1,000,000, получено {v}"
            )
        return round(v, 2)


class CurrencyResponse(CurrencyRequest):
    id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class SortField(str, Enum):
    ID = "id"
    NAME = "name"
    SHORT_NAME = "short_name"
    VALUE = "value"

class CurrencyUpdate(BaseModel):
     name: Optional[str] = None
     short_name: Optional[str] = Field(None, max_length=3)
     value: Optional[float] = None

     @field_validator('short_name')
     def validate_short_name(cls, v):
        if v is not None and len(v) > 3:
            raise ValueError(f"Максимальная длина 3 символа, получено {len(v)}")
        return v.upper() if v else v

     @field_validator('value')
     def validate_value(cls, v):
         if v is not None and v <= 0:
           raise ValueError(f"Значение должно быть больше 0, получено {v}")
         return v