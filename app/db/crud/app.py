# -*- coding: utf-8 -*-
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import App
from app.schemas import AppCreate, AppUpdate
from .base import CRUDBase

class CRUDApp(CRUDBase[App, AppCreate, AppUpdate]):
    pass


app = CRUDApp(App)
