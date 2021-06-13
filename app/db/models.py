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
    path = Column(String(100), unique=True)
    title = Column(String(100))
    description = Column(String(100))
    enabled = Column(Boolean, default=True)
    entrypoint = Column(String(200))

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
    name = Column(String(100), index=True)
    title = Column(String(100))
    image = Column(String(100))
    container_id = Column(String(100))
    network = Column(String(100))
    ip = Column(String(100))
    version = Column(Integer, default=1)
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
    
    users = relationship("User",
                        primaryjoin="Role.id==foreign(Authorized.role_id)",
                        secondaryjoin="and_(User.id==foreign(Authorized.user_id),Authorized.data_enabled==True)",
                        secondary='authorized',
                        viewonly=True
                        )

    data_enabled = Column(Boolean, default=True)
    data_created_at = Column(DateTime,default=datetime.utcnow)
    data_updated_at = Column(DateTime,onupdate=datetime.utcnow)
    data_deleted_at = Column(DateTime)
    data_created_by = Column(Integer)
    data_updated_by = Column(Integer)
    data_deleted_by = Column(Integer)

    @property
    def auth(self):
        """
        prevent pydantic model auto translate json string to dict
        """
        #return json.loads(self._auth)
        return str(self._auth)

    @auth.setter
    def auth(self, value):
        self._auth = json.dumps(value,ensure_ascii=False)
    

class Authorized(Base):
    __tablename__ = "authorized"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    role_id = Column(Integer, index=True)
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
    display_name = Column(String(100))
    enabled = Column(Boolean, default=True)
    _password = Column("password",String(100))
    is_admin = Column(Boolean, default=True)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = get_password_hash(value)

    roles = relationship("Role",
                        primaryjoin="User.id==foreign(Authorized.user_id)",
                        secondaryjoin="and_(Role.id==foreign(Authorized.role_id),Authorized.data_enabled==True)",
                        secondary='authorized',
                        viewonly=True
                        )


class ThirdUser(Base):
    __tablename__ = "third_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    third = Column(String(100), index=True)
    third_user_id = Column(String(100), index=True)
    third_user_name = Column(String(100))
    user_id = Column(Integer)
    binded_at =Column(DateTime,default=datetime.utcnow)

