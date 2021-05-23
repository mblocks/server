# -*- coding: utf-8 -*-
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models import User, Authorized, App
from app.schemas import UserCreate, UserUpdate
from .base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def before_create(self, db: Session, *, obj_in):
        del obj_in.apps

    def after_create(self, db: Session, *, db_obj, obj_in):
        for item_app in obj_in.apps:
            for item_role in item_app.roles:
                db.add(Authorized(
                    user_id=db_obj.id,
                    role_id=item_role.id,
                ))

    def get(self, db: Session, id: int) -> Optional[User]:
        user = super().get(db=db, id=id)
        find_apps = []
        apps_roles = {}
        for item in user.roles:
            find_apps.append(item.parent_id)
            if not apps_roles.get(item.parent_id):
                apps_roles[item.parent_id] = []
            apps_roles[item.parent_id].append(item)

        apps = []
        for item in db.query(App).filter(App.id.in_(find_apps)).all():
            item.roles = apps_roles[item.id]
            apps.append(item)
        
        user.apps = apps
        return user


user = CRUDUser(User)
