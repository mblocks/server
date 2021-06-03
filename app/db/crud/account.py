# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas import AccountCreate, AccountUpdate
from .base import CRUDBase

class CRUDAccount(CRUDBase[User, AccountCreate, AccountUpdate]):
    def before_create(self, db: Session, *, obj_in):
        if obj_in.display_name is None:
            obj_in.display_name = obj_in.user_name

account = CRUDAccount(User)
