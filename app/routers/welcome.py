# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from app import deps, config, schemas
from app.db import crud
from app.utils import verify_password
from app.db.cache import generate_apikey

router = APIRouter()


@router.get("/", response_model=schemas.Welcome)
async def index(db: Session = Depends(deps.get_db)):
    return crud.account.get_welcome(db)

@router.post("/join", response_model=schemas.Welcome)
async def join(response: Response,
               payload: schemas.AccountCreate,
               db: Session = Depends(deps.get_db)):
    if crud.account.count(db, search={'user_name': payload.user_name}) > 0:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "user_name"],
                "msg": "user_name already registered",
                "type": "value_error"
            },
        ])
    account = crud.account.create(db=db, obj_in=payload)
    apikey = generate_apikey(account)
    response.set_cookie(key="apikey", value=apikey)
    return crud.get_welcome(db, user=account)

@router.post("/login", response_model=schemas.Welcome)
async def login(response: Response,
               payload: schemas.AccountLogin,
               db: Session = Depends(deps.get_db)):
    find_user = crud.account.find(db, search={'user_name': payload.user_name})
    if not find_user:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "user_name"],
                "msg": "user_name is not exists",
                "type": "value_error"
            },
        ])
    if not verify_password(payload.password, find_user.password):
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "password"],
                "msg": "password is correct",
                "type": "value_error"
            },
        ])
    
    apikey = generate_apikey(find_user)
    response.set_cookie(key="apikey", value=apikey)
    return crud.account.get_welcome(db, user=find_user)


