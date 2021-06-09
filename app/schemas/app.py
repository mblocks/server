from typing import Optional, List
from pydantic import BaseModel
from .service import Service, ServiceLite, ServiceCreate
from .base import DBBase
from .role import RoleLite


# Shared properties
class AppBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    path: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = True
    endpoint: Optional[str] = None


class AppCreate(AppBase):
    name: str
    title: str
    services: List[ServiceCreate]


class AppUpdate(AppBase):
    pass


class App(AppBase, DBBase):
    services: List[Service] = []
    roles: List[RoleLite] = []


class AppLite(AppBase, DBBase):
    services: List[ServiceLite] = []


class AppList(BaseModel):
    data: List[AppLite]
    total: Optional[int] = 0
