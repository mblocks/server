# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.db import cache


router = APIRouter()

@router.get("/authorized")
async def get_authorized(user_id: int):
    return cache.get_authorized(user_id=user_id)
