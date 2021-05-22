# -*- coding: utf-8 -*-
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import Service
from app.schemas import ServiceCreate, ServiceUpdate
from .base import CRUDBase

class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    pass


service = CRUDService(Service)

