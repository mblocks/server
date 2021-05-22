from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from .service import Service


# Shared properties
class AppBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = True
    endpoint: Optional[str] = None
    services: List[Service] = []


class AppCreate(AppBase):
    name: str
    title: str
    services: List[Service]


class AppUpdate(AppBase):
    pass


class AppInDBBase(AppBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class App(AppInDBBase):
    pass


class AppList(BaseModel):
    data: List[App]
    total: Optional[int] = 0
