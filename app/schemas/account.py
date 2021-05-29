from typing import Optional
from pydantic import BaseModel
from .base import DBBase


class AccountCreate(BaseModel):
    user_name: str
    password: str


class AccountUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class Account(DBBase):
    user_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
