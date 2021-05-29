from typing import Optional, List
from pydantic import BaseModel, Json
from .base import DBBase


class RoleBase(BaseModel):
    parent_id: Optional[int] = None
    title: Optional[str] = None
    auth: Optional[Json] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class Role(RoleBase, DBBase):
    pass


class RoleLite(DBBase):
    title: Optional[str] = None
   

class RoleList(BaseModel):
    data: List[Role]
    total: Optional[int] = 0
