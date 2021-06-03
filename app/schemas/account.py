from typing import Optional
from pydantic import BaseModel

class AccountLogin(BaseModel):
    user_name: str
    password: str


class AccountCreate(AccountLogin):
    display_name: Optional[str] = None
    email: Optional[str] = None


class AccountUpdate(AccountCreate):
    password: Optional[str] = None



