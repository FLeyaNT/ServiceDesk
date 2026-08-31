from pydantic import BaseModel, Field
from enum import Enum

from models.users import UserRole


class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100
    )
    full_name: str = Field(
        ...,
        max_length=255
    )
    role: UserRole = Field(
        default=UserRole.EMPLOYEE
    )


class LoginRequest(BaseModel):
    username: str
    password: str


class UserBaseResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole

    class Config:
        from_attributes = True


class UserShortResponse(UserBaseResponse):
    pass
