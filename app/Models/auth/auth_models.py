from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.Models.role.role_types import RoleTypeResponse


class UserCreate(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    age: int = Field(...)


class UserResponse(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    is_active: bool = Field(alias="isactive")
    id: Optional[int] = None

    class Config:
        from_attributes = True


class CurrentUserResponse(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    is_active: bool = Field(alias="isactive")
    id: Optional[int] = None
    content: Optional[str] = None
    role: Optional[RoleTypeResponse] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True

class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    id: Optional[int] = None
    content: Optional[str] = None
    role_id: Optional[int] = None
    age: Optional[int] = None

    class Config:
        from_attributes = True


class UserWrapper(BaseModel):
    user: UserResponse


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


class Login(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class LoginResponse(BaseModel):
    message: str
    refresh_token: str | None = None
    access_token: str | None = None


class AuthMessage(BaseModel):
    message: str


class ResetPasswordResponse(BaseModel):
    new_password: str = Field(...)
    prev_password: str = Field(...)
    email: EmailStr = Field(...)


class ResetResponse(BaseModel):
    message: str
