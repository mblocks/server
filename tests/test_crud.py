# -*- coding: utf-8 -*-
from app.db import crud
from app.schemas import AppCreate, AppUpdate

def test_app_create(db):
    app = crud.app.create(db=db, obj_in=AppCreate(
        name='hello1',title='hello1',enabled=True,endpoint='http://10.12.32.54'
    ))
    find_app = crud.app.get(db=db, id=app.id)
    assert find_app.name == app.name

def test_app_update(db):
    app = crud.app.create(db=db, obj_in=AppCreate(
        name='hello2',title='hello2',enabled=True,endpoint='http://10.12.32.54'
    ))
    crud.app.update(db=db, db_obj=app, obj_in=AppUpdate(name='hello2-updated'))
    find_app = crud.app.get(db=db, id=app.id)
    assert app.name == find_app.name

def test_app_remove(db):
    app = crud.app.create(db=db, obj_in=AppCreate(
        name='hello3',title='hello3',enabled=True,endpoint='http://10.12.32.54'
    ))
    crud.app.remove(db=db, id=app.id)
    find_app = crud.app.get(db=db, id=app.id)
    assert find_app is None

