# -*- coding: utf-8 -*-
from typing import List
from fastapi import APIRouter, Depends, Query
from app import deps
from app.db import cache



router = APIRouter()

@router.get("/authorized")
async def get_authorized(user_id: int,
                         app_id: List[int] = Query(...),
                         redis_client = Depends(deps.get_redis)
                        ):
    return cache.get_authorized(user_id=user_id)

