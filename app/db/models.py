# -*- coding: utf-8 -*-
import json
from typing import TYPE_CHECKING
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.utils import get_password_hash


class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True)
    title = Column(String(100))
    description = Column(String(100))
    enabled = Column(Boolean, default=True)
    endpoint = Column(String(200))

    data_enabled = Column(Boolean, default=True)
    data_created_at = Column(DateTime,default=datetime.utcnow)
    data_updated_at = Column(DateTime,onupdate=datetime.utcnow)
    data_deleted_at = Column(DateTime)
    data_created_by = Column(Integer)
    data_updated_by = Column(Integer)
    data_deleted_by = Column(Integer)

    services = relationship("Service",
                        primaryjoin="App.id==foreign(Service.parent_id)",
                        lazy='selectin'
                        )

    
class Service(Base):
    __tablename__ = "apps_services"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, index=True)
    name = Column(String(100), unique=True, index=True)
    title = Column(String(100))
    image = Column(String(100))
    container_id = Column(String(100), default=True)
    ip = Column(String(100))
    _environment = Column("environment",String(400))

    data_enabled = Column(Boolean, default=True)
    data_created_at = Column(DateTime,default=datetime.utcnow)
    data_updated_at = Column(DateTime,onupdate=datetime.utcnow)
    data_deleted_at = Column(DateTime)
    data_created_by = Column(Integer)
    data_updated_by = Column(Integer)
    data_deleted_by = Column(Integer)

    @property
    def environment(self):
        return json.loads(self._environment)

    @environment.setter
    def environment(self, value):
        # https://docs.sqlalchemy.org/en/14/orm/mapped_attributes.html#using-custom-datatypes-at-the-core-level
        self._environment = json.dumps(jsonable_encoder(value))


class Role(Base):
    __tablename__ = "apps_roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, index=True)
    title = Column(String(100))
    description = Column(String(400))
    _auth = Column("auth",String(800))
    enabled = Column(Boolean, default=True)
    
    users = relationship("User", secondary='authorized', back_populates="roles")

    data_enabled = Column(Boolean, default=True)
    data_created_at = Column(DateTime,default=datetime.utcnow)
    data_updated_at = Column(DateTime,onupdate=datetime.utcnow)
    data_deleted_at = Column(DateTime)
    data_created_by = Column(Integer)
    data_updated_by = Column(Integer)
    data_deleted_by = Column(Integer)

    @property
    def auth(self):
        return json.loads(self._auth)

    @auth.setter
    def auth(self, value):
        self._auth = json.dumps(value,ensure_ascii=False)
    

class Authorized(Base):
    __tablename__ = "authorized"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    role_id = Column(Integer, ForeignKey("apps_roles.id"), index=True)
    app_id = Column(Integer)

    data_enabled = Column(Boolean, default=True)
    data_created_at = Column(DateTime,default=datetime.utcnow)
    data_updated_at = Column(DateTime,onupdate=datetime.utcnow)
    data_deleted_at = Column(DateTime)
    data_created_by = Column(Integer)
    data_updated_by = Column(Integer)
    data_deleted_by = Column(Integer)



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(100), unique=True, index=True)
    email = Column(String(100), index=True)
    enabled = Column(Boolean, default=True)
    _password = Column("password",String(100))

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = get_password_hash(value)

    roles = relationship("Role", primaryjoin="and_(Role.id==Authorized.role_id, Authorized.data_enabled==True)", secondary='authorized', back_populates="users")
