from typing import Optional, List
from pydantic import BaseModel
from .role import Role


class AppRoles(BaseModel):
    id: int
    name: Optional[str] = None
    title: Optional[str] = None
    roles: List[Role] = []


class UserBase(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    enabled: Optional[bool] = True
    apps: List[AppRoles] = []


class UserCreate(UserBase):
    user_name: str
    email: str


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserList(BaseModel):
    data: List[User]
    total: Optional[int] = 0
