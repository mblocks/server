# -*- coding: utf-8 -*-
from app.db.models import Role
from app.schemas import RoleCreate, RoleUpdate
from .base import CRUDBase

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    pass

role = CRUDRole(Role)
