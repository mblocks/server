# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base


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
    container_id = Column(Boolean, default=True)
    ip = Column(String(100))

    data_enabled = Column(Boolean, default=True)
    data_created_at = Column(DateTime,default=datetime.utcnow)
    data_updated_at = Column(DateTime,onupdate=datetime.utcnow)
    data_deleted_at = Column(DateTime)
    data_created_by = Column(Integer)
    data_updated_by = Column(Integer)
    data_deleted_by = Column(Integer)

    
