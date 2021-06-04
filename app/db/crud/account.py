# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas import AccountCreate, AccountUpdate, Userinfo
from .base import CRUDBase

class CRUDAccount(CRUDBase[User, AccountCreate, AccountUpdate]):
    def before_create(self, db: Session, *, obj_in):
        if obj_in.display_name is None:
            obj_in.display_name = obj_in.user_name

    def get_welcome(self, db: Session, *, user = None):
        res = {
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg',
            'title': 'Welcome',
            'description': 'Hello'
        }
        if user:
            res['userinfo'] = Userinfo(display_name=user.display_name)
        return res

account = CRUDAccount(User)
