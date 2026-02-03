from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class User(BaseModel):
    name: str
    id: int
    age: int
    password: str
    is_adult: bool = False


class Login(BaseModel):
    name: str = Field(...)
    password: str = Field(...)


FORBIDDEN_WORDS = ["редиска", "бяка", "козявка"]


class Contact(BaseModel):
    email: EmailStr = Field(...)
    phone: Optional[int] = None

    @field_validator("phone")
    def validate_phone(cls, value: int | None) -> int | None:
        phone = str(value).lower()
        if len(phone) < 7:
            raise ValueError("Количество знаков не может быть меньше 7")
        elif len(phone) > 15:
            raise ValueError("Количество знаков не может быть больше 15")
        return value


class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)
    contact: Contact = Field(...)

    @field_validator("message")
    def validate_message(cls, value: str):
        text = value.lower()

        for word in FORBIDDEN_WORDS:
            if word in text:
                raise ValueError("Использование недопустимых слов")

        return value


class FeedbackResponse(BaseModel):
    message: str
    feedback: Feedback


class UserCreate(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    age: int = Optional[int]
    is_subscribed: Optional[bool] = None

    @field_validator("age")
    def validate_age(cls, value: int | None) -> int | None:
        if value is None:
            return value
        elif value < 0:
            raise ValueError("Значение возрасто должно быть больше 0")


class Product(BaseModel):
    id: int = Field(...)
    name: str = Field(...)
