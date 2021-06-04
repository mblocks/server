# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import config, deps, schemas
from app.utils import verify_password
from app.db import crud

router = APIRouter()


@router.get('/whoami')
async def whoami(db: Session = Depends(deps.get_db)):
    return crud.account.get_welcome(db)

@router.get('/settings/userinfo', response_model=schemas.Userinfo)
async def get_userinfo(current_user = Depends(deps.get_current_user), 
                       db: Session = Depends(deps.get_db)
                      ):
    find_account = crud.account.get(db, id=current_user.id)
    return find_account

@router.post('/settings/userinfo', response_model=schemas.Userinfo)
async def update_userinfo(payload: schemas.Userinfo,
                          current_user = Depends(deps.get_current_user), 
                          db: Session = Depends(deps.get_db)
                         ):
    find_account = crud.account.get(db, id=current_user.id)
    return crud.account.update(db, db_obj=find_account, obj_in=payload)

@router.post('/settings/security/password')
async def update_password(payload: schemas.AccountChangePassword,
                          current_user = Depends(deps.get_current_user),
                          db: Session = Depends(deps.get_db)
                        ):
    find_account = crud.account.get(db, id=current_user.id)
    if not verify_password(payload.password, find_account.password):
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "password"],
                "msg": "password is correct",
                "type": "value_error"
            },
        ])
    crud.account.update(db, db_obj=find_account, obj_in={'password':payload.new_password})
    return { 'result': True }
