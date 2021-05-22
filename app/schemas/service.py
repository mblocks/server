from typing import Optional, List
from pydantic import BaseModel, HttpUrl


# Shared properties
class ServiceBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    image: Optional[str] = None
    container_id: Optional[str] = None
    ip: Optional[str] = None


class ServiceCreate(ServiceBase):
    name: str
    title: str


class ServiceUpdate(ServiceBase):
    pass


class ServiceInDBBase(ServiceBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class Service(ServiceInDBBase):
    pass


class ServiceList(BaseModel):
    data: List[Service]
    total: Optional[int] = 0
