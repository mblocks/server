# -*- coding: utf-8 -*-
from sqlalchemy.orm import Session
from app.db import cache
from app.db.models import User
from app.schemas import AccountCreate, AccountUpdate
from .base import CRUDBase

class CRUDAccount(CRUDBase[User, AccountCreate, AccountUpdate]):
    def before_create(self, db: Session, *, obj_in):
        if obj_in.display_name is None:
            obj_in.display_name = obj_in.user_name

    def get_welcome(self, db: Session, *, current_user = None):
        res = {
            'logo': 'https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg',
            'title': 'Welcome',
            'description': 'Hello'
        }
        if current_user:
            res['userinfo'] = {
                'display_name':current_user.display_name,
                'apps':list(cache.get_authorized(user_id=current_user.id).values())
            }
        return res

account = CRUDAccount(User)
