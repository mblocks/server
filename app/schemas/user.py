from typing import Optional, List
from pydantic import BaseModel
from .base import DBBase
from .role import RoleLite


class AppRoles(BaseModel):
    id: int
    name: Optional[str] = None
    title: Optional[str] = None
    roles: List[RoleLite] = []


class UserBase(BaseModel):
    user_name: Optional[str] = None
    email: Optional[str] = None
    enabled: Optional[bool] = None


class UserUpdate(UserBase):
    password: Optional[str] = None
    apps: List[AppRoles] = []


class UserCreate(UserUpdate):
    user_name: str
    email: str


class User(UserUpdate, DBBase):
    pass


class UserLite(UserBase, DBBase):
    pass


class UserList(BaseModel):
    data: List[UserLite]
    total: Optional[int] = 0


class CurrentUser(BaseModel):
    id: Optional[int] = None
    third: Optional[str] = None
    third_user_id: Optional[str] = None
    third_user_name: Optional[str] = None
    is_admin: Optional[bool] = True


class Userinfo(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True
