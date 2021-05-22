# -*- coding: utf-8 -*-
from app.db import crud
from app.schemas import AppCreate

def test_flows_query(db):
    app = crud.app.create(db=db, obj_in=AppCreate(
        name='hello1',title='hello1',enabled=True,endpoint='http://10.12.32.54'
    ))
    find_app = crud.app.get(db=db, id=app.id)
    assert find_app.name == app.name

