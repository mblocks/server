from typing import Optional
from pydantic import BaseModel, Json


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


class RoleInDBBase(RoleBase):
    id: int

    class Config:
        orm_mode = True


class Role(RoleInDBBase):
    pass
