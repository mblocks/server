# -*- coding: utf-8 -*-
import os
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base  # noqa: F401


database_url = os.getenv("SQLALCHEMY_DATABASE_URI", 'sqlite://')
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=True,
    connect_args={"check_same_thread": False} if 'sqlite' in database_url else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def pytest_configure(config):
    pass

@pytest.fixture(autouse=True)
def init_db(monkeypatch):
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="session")
def db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
