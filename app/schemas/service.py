from typing import Optional, List
from pydantic import BaseModel
from .base import DBBase


class Environment(BaseModel):
    name: str
    value: str


class ServiceBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    image: Optional[str] = None
    environment: List[Environment] = []
    parent_id: Optional[int] = None
    version: Optional[int] = None


class ServiceCreate(ServiceBase):
    name: str
    image: str


class ServiceUpdate(ServiceBase):
    pass


class Service(ServiceBase, DBBase):
    container_id: Optional[str] = None
    ip: Optional[str] = None
    network: Optional[str] = None
    status: Optional[str] = None


class ServiceLite(DBBase):
    name: Optional[str] = None
    title: Optional[str] = None
    image: Optional[str] = None
    status: Optional[str] = None


class ServiceList(BaseModel):
    data: List[Service]
    total: Optional[int] = 0
