# -*- coding: utf-8 -*-
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import deps, config, schemas
from app.db import crud

router = APIRouter()


@router.get("/apps", response_model=schemas.AppList)
async def query_apps(db: Session = Depends(deps.get_db),
                     name: Optional[str] = None,
                     enabled: Optional[bool] = None,
                     skip: int = 0,
                     limit: int = 100,
                     total: int = None
                     ):
    search = {'name': name, 'enabled': enabled}
    apps = crud.app.get_multi(db, search=search, skip=skip, limit=limit)
    if not total:
        total = crud.app.count(db, search=search)
    return schemas.AppList(data=apps, total=total)


@router.post("/apps", response_model=schemas.App)
async def create_app(payload: schemas.AppCreate,
                     db: Session = Depends(deps.get_db)
                     ):
    if crud.app.count(db, search={'name': payload.name}) > 0:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "name"],
                "msg": "name already registered",
                "type": "value_error"
            },
        ])
    return crud.app.create(db=db, obj_in=payload)


@router.get("/apps/roles")
async def query_apps_roles(db: Session = Depends(deps.get_db)):
    return crud.app.get_multi_with_roles(db)


@router.get("/apps/{app_id}", response_model=schemas.App)
async def get_app(app_id: int, db: Session = Depends(deps.get_db)):
    find_app = crud.app.get(db, id=app_id)
    if find_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    return find_app


@router.get("/apps/{app_id}/overview", response_model=schemas.App)
async def get_app(app_id: int, db: Session = Depends(deps.get_db)):
    find_app = crud.app.get(db, id=app_id)
    if find_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    return find_app


@router.post("/apps/{app_id}", response_model=schemas.App)
async def update_app(app_id: int,
                     payload: schemas.AppUpdate,
                     db: Session = Depends(deps.get_db)
                     ):
    app = crud.app.get(db, id=app_id)
    if not app:
        raise HTTPException(
            status_code=404,
            detail="The app with this app_id does not exist in the system",
        )
    if crud.app.count(db, search={'id !=': app_id, 'name': payload.name}) > 0:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "name"],
                "msg": "app name has same name",
                "type": "value_error"
            },
        ])
    return crud.app.update(db, db_obj=app, obj_in=payload)


@router.get("/apps/{app_id}/roles", response_model=schemas.RoleList)
async def query_app_roles(app_id: int,
                          title: Optional[str] = None,
                          total: int = None,
                          db: Session = Depends(deps.get_db)
                          ):
    search = {"parent_id": app_id, "title": title}
    roles = []
    for item in crud.role.get_multi(db, search=search):
        roles.append(schemas.Role.construct(id=item.id,
                                            parent_id=item.parent_id,
                                            title=item.title,
                                            auth=item.auth,
                                            description=item.description,
                                            enabled=item.enabled
                                            ))

    if not total:
        total = crud.role.count(db, search=search)
    return schemas.RoleList(data=roles, total=total)


@router.post("/apps/{app_id}/roles", response_model=schemas.Role)
async def create_app_role(app_id: int,
                          payload: schemas.RoleCreate,
                          db: Session = Depends(deps.get_db)
                          ):
    payload.parent_id = app_id
    return crud.role.create(db=db, obj_in=payload)


@router.post("/apps/{app_id}/roles/{role_id}", response_model=schemas.Role)
async def update_app_role(app_id: int,
                          role_id: int,
                          payload: schemas.RoleUpdate,
                          db: Session = Depends(deps.get_db)
                          ):
    find_role = crud.role.get(db, id=role_id)
    return crud.role.update(db=db, db_obj=find_role, obj_in=payload)


@router.post("/apps/{app_id}/roles/{role_id}/delete", response_model=schemas.Role)
async def delete_app_role(app_id: int,
                          role_id: int,
                          db: Session = Depends(deps.get_db)
                          ):
    return crud.role.remove(db=db, id=role_id)


@router.post("/apps/{app_id}/services", response_model=schemas.Service)
async def create_app_service(app_id: int,
                             payload: schemas.ServiceCreate,
                             db: Session = Depends(deps.get_db)
                             ):
    if crud.service.count(db, search={'parent_id': app_id, 'name': payload.name}) > 0:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body", "name"],
                "msg": "service name exists",
                "type": "value_error"
            },
        ])
    payload.parent_id = app_id
    return crud.service.create(db=db, obj_in=payload)


@router.post("/apps/{app_id}/services/{service_id}", response_model=schemas.Service)
async def update_app_service(app_id: int,
                             service_id: int,
                             payload: schemas.ServiceUpdate,
                             db: Session = Depends(deps.get_db)
                             ):
    find_service = crud.service.get(db, id=service_id)
    return crud.service.update(db=db, db_obj=find_service, obj_in=payload)


@router.post("/apps/{app_id}/services/{service_id}/delete", response_model=schemas.Service)
async def delete_app_service(app_id: int,
                             service_id: int,
                             db: Session = Depends(deps.get_db)
                             ):
    return crud.service.remove(db=db, id=service_id)


@router.get("/users", response_model=schemas.UserList)
async def query_apps(db: Session = Depends(deps.get_db),
                     user_name: Optional[str] = None,
                     email: Optional[str] = None,
                     skip: int = 0,
                     limit: int = 100,
                     total: int = None
                     ):
    search = {'user_name': user_name, 'email': email}
    users = crud.user.get_multi(db, search=search, skip=skip, limit=limit)
    if not total:
        total = crud.user.count(db, search=search)
    return schemas.UserList(data=users, total=total)


@router.get("/users/{user_id}", response_model=schemas.User)
async def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    find_user = crud.user.get_multi_with_roles(db, id=user_id)
    if find_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return find_user


@router.post("/users/{user_id}", response_model=schemas.User)
async def create_user(user_id: int,
                      payload: schemas.UserUpdate,
                      db: Session = Depends(deps.get_db)
                      ):
    find_user = crud.user.get(db=db, id=user_id)
    return crud.user.update(db=db, db_obj=find_user, obj_in=payload)


@router.post("/users/{user_id}/delete", response_model=schemas.User)
async def delete_user(user_id: int,
                      db: Session = Depends(deps.get_db)
                      ):
    return crud.user.remove(db=db, id=user_id)
