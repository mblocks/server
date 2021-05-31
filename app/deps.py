# -*- coding: utf-8 -*-
from fastapi import Request, HTTPException
from app.db.session import SessionLocal, redis_client
from app.schemas import CurrentUser
from app.db.cache import get_authorized

def get_redis():
    return redis_client

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request):
    return CurrentUser(id=request.headers.get('x-consumer-user-id'),
                       third=request.headers.get('x-consumer-third'),
                       third_user_id=request.headers.get('x-consumer-third-user-id'),
                       third_user_name=request.headers.get('x-consumer-third-user-name','').encode("Latin-1").decode("utf-8"),
                      )

def verify_user(request: Request):
    user_id = request.headers.get('x-consumer-user-id',1)
    if not user_id:
        raise HTTPException(status_code=401, detail="you can not access")

    if '1' not in get_authorized(user_id=user_id):
        raise HTTPException(status_code=403, detail="you can not access")

