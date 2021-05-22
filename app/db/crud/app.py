# -*- coding: utf-8 -*-
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import App, Service
from app.schemas import AppCreate, AppUpdate
from .base import CRUDBase

class CRUDApp(CRUDBase[App, AppCreate, AppUpdate]):
    def before_create(self, db: Session, *, obj_in):
        del obj_in.services

    def after_create(self, db: Session, *, db_obj, obj_in):
        for item in obj_in.services:
            db.add(Service(
                parent_id=db_obj.id,
                name=item.name,
                title=item.title,
                image=item.image
            ))


app = CRUDApp(App)
