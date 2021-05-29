from typing import Optional, List
from pydantic import BaseModel


class Environment(BaseModel):
    name: str
    value: str


class ServiceBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    image: Optional[str] = None
    container_id: Optional[str] = None
    ip: Optional[str] = None
    environment: List[Environment] = []
    status: Optional[str] = None
    parent_id: Optional[int] = None


class ServiceCreate(ServiceBase):
    name: str
    image: str


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
