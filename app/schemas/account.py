from typing import Optional, List
from pydantic import BaseModel
from .role import Role


class AccountBase(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    

class AccountCreate(BaseModel):
    user_name: str
    password: str


class AccountUpdate(BaseModel):
    email: str
    password: str


class AccountInDBBase(AccountBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class Account(AccountInDBBase):
    pass

