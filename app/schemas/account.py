from typing import Optional
from pydantic import BaseModel
from .base import DBBase

class AccountBase(BaseModel):
    display_name: Optional[str] = None

class AccountCreate( AccountBase):
    user_name: str
    password: str


class AccountUpdate(AccountBase):
    email: Optional[str] = None
    password: Optional[str] = None


class Account(DBBase, AccountBase):
    user_name: Optional[str] = None
    email: Optional[str] = None


class AccountLite(AccountBase):
    pass
