# -*- coding: utf-8 -*-
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app import deps, utils



router = APIRouter()

@router.get("/authorized")
async def get_authorized(user_id: int,
                         app_id: List[int] = Query(...),
                         redis_client = Depends(deps.get_redis)
                        ):
    return utils.get_authorized(user_id=user_id,app_id=app_id)

