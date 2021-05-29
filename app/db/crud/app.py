# -*- coding: utf-8 -*-
from typing import Dict, List
from sqlalchemy.orm import Session
from app.db.models import App, Service, Role
from app.schemas import app as schemas
from .base import CRUDBase

class CRUDApp(CRUDBase[App, schemas.AppCreate, schemas.AppUpdate]):
    def before_create(self, db: Session, *, obj_in):
        del obj_in.services

    def after_create(self, db: Session, *, db_obj, obj_in):
        for item in obj_in.services:
            db.add(Service(
                parent_id=db_obj.id,
                name=item.name,
                title=item.title,
                image=item.image,
                environment =item.environment
            ))

    def get_multi_with_roles(
        self,
        db: Session,
    ) -> List[schemas.App]:
        res = {}
        query_apps = db.query(App).with_entities(App.id,App.name,App.title).filter(App.data_enabled==True).all()
        query_roles = db.query(Role).with_entities(Role.id, Role.title, Role.parent_id).filter(Role.data_enabled==True).all()
        roles = {}
        for item in query_roles:
            if not roles.get(item.parent_id):
                roles[item.parent_id]=[]
            roles[item.parent_id].append({'id':item.id,'title':item.title})

        for item in query_apps:
            res[item.name] = {'id':item.id,
                        'name': item.name,
                        'title': item.title,
                        'roles': roles.get(item.id,[])
                       }
        return res

app = CRUDApp(App)
