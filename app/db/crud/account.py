# -*- coding: utf-8 -*-
from app.db.models import User
from app.schemas import AccountCreate, AccountUpdate
from .base import CRUDBase

class CRUDAccount(CRUDBase[User, AccountCreate, AccountUpdate]):
    pass

account = CRUDAccount(User)
