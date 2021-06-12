# -*- coding: utf-8 -*-
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from . import routers, deps

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routers.admin, tags=["admin"], prefix='/admin', dependencies=[ Depends(deps.verify_user) ])
app.include_router(routers.welcome, tags=["welcome"], prefix='/welcome')
app.include_router(routers.settings, tags=["settings"])
app.include_router(routers.authorized, tags=["authorized"])
