# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.db.models import Service
from app.schemas import ServiceCreate, ServiceUpdate
from .base import CRUDBase

class CRUDService(CRUDBase[Service, ServiceCreate, ServiceUpdate]):
    def update(
        self,
        db: Session,
        *,
        db_obj: Service,
        obj_in: ServiceUpdate
    ) -> Service:
        obj_in.version =db_obj.version + 1
        return super().update(db, db_obj=db_obj, obj_in=obj_in)


service = CRUDService(Service)

