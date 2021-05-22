# -*- coding: utf-8 -*-
from app.db.session import SessionLocal, redis_client

def get_redis():
    return redis_client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
