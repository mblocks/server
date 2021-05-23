# -*- coding: utf-8 -*-
import json
from app.db import crud
from app.schemas import AppCreate, AppUpdate, Service, Environment

def test_app_create(db):
    app = crud.app.create(db=db, obj_in=AppCreate(
        name='hello1',
        title='hello1',
        enabled=True,
        endpoint='http://10.12.32.54',
        services=[
            Service(name='main',title='main-title',image='nginx:alpine',environment=[Environment(name='DB_HOST',value='127.0.0.1')]),
            Service(name='other',title='other-title',image='nginx:alpine')
        ]
    ))
    find_app = crud.app.get(db=db, id=app.id)
    first_service = find_app.services[0]
    assert find_app.name == app.name
    assert isinstance(find_app.services ,list)
    assert len(find_app.services) == 2
    assert isinstance(first_service.environment ,list)

def test_app_update(db):
    app = crud.app.create(db=db, obj_in=AppCreate(
        name='hello2',
        title='hello2',
        enabled=True,
        endpoint='http://10.12.32.54',
        services=[]
    ))
    crud.app.update(db=db, db_obj=app, obj_in=AppUpdate(name='hello2-updated'))
    find_app = crud.app.get(db=db, id=app.id)
    assert app.name == find_app.name

def test_app_remove(db):
    app = crud.app.create(db=db, obj_in=AppCreate(
        name='hello3',
        title='hello3',
        enabled=True,
        endpoint='http://10.12.32.54',
        services=[]
    ))
    crud.app.remove(db=db, id=app.id)
    find_app = crud.app.get(db=db, id=app.id)
    assert find_app is None

