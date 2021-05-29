# -*- coding: utf-8 -*-
import json
from app.db import crud
from app.utils import verify_password
from app.schemas import AppCreate, AppUpdate, Service, UserCreate, UserUpdate, Role, RoleCreate, AccountCreate, AccountUpdate


def test_app_create(db):
    app = crud.app.create(db=db, obj_in=AppCreate.parse_obj({
        'name': 'hello1',
        'title': 'hello1',
        'services': [
                {'name': 'main',
                    'title': 'main-title',
                    'image': 'nginx:alpine',
                    'environment': [
                        {'name': 'DB_HOST', 'value': '127.0.0.1'}
                    ]
                 },
                {'name': 'other',
                    'title': 'other-title',
                    'image': 'nginx:alpine'
                 }
        ]
    }))
    find_app = crud.app.get(db=db, id=app.id)
    first_service = find_app.services[0]
    assert find_app.name == app.name
    assert isinstance(find_app.services, list)
    assert len(find_app.services) == 2
    assert isinstance(first_service.environment, list)


def test_app_update(db):
    app = crud.app.create(db=db, obj_in=AppCreate.parse_obj({
        'name': 'hello2',
        'title': 'hello2',
        'services': []
    }))
    crud.app.update(db=db, db_obj=app, obj_in=AppUpdate(name='hello2-updated'))
    find_app = crud.app.get(db=db, id=app.id)
    assert app.name == find_app.name


def test_app_remove(db):
    app = crud.app.create(db=db, obj_in=AppCreate.parse_obj({
        'name': 'hello3',
        'title': 'hello3',
        'services': []
    }))
    crud.app.remove(db=db, id=app.id)
    find_app = crud.app.get(db=db, id=app.id)
    assert find_app is None


def test_app_role_create(db):
    role = crud.role.create(db=db, obj_in=RoleCreate.parse_obj({
        'parent_id': 1,
        'title': 'role1',
        'auth': '{"query":200}'
    }))
    find_role = crud.role.get(db=db, id=role.id)
    assert role.title == find_role.title


def test_user_create(db):
    user = crud.user.create(db=db, obj_in=UserCreate.parse_obj({
        'user_name': 'hello1',
        'email': 'hello1@mblocks.com',
        'apps': [
            {
                'name': 'app1',
                'title': 'app1-title',
                'id': 1,
                'roles': [
                            {'id': 1, 'title': 'role1'}
                        ]
            }
        ]
    }))
    find_user = crud.user.get(db, user.id)
    first_app = find_user.apps[0]
    first_role = first_app.roles[0]
    assert first_app.name == 'hello1'
    assert isinstance(first_app.roles, list)
    assert first_role.title == 'role1'
    assert first_role.id == 1


def test_user_update(db):
    user = crud.user.get(db=db, id=1)
    crud.user.update(db=db, db_obj=user, obj_in=UserUpdate.parse_obj({
        'user_name':'hello1_new',
        'apps': [
            {
                'name': 'app1',
                'title': 'app1-title',
                'id': 1,
                'roles': []
            }
        ]
    }))

    find_user = crud.user.get(db, id=1 )
    assert find_user.user_name == user.user_name
    assert len(find_user.apps)== 0


def test_account_create(db):
    account = crud.account.create(db=db, obj_in=AccountCreate.parse_obj({
        'user_name': 'account1',
        'password': '123456',
    }))
    find_account = crud.account.get(db, account.id)
    assert account.user_name == find_account.user_name
    assert verify_password('123456',account.password)
