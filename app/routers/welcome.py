# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from app import deps, config

router = APIRouter()

@router.get("/initdata")
async def get_initdata(settings: config.Settings = Depends(config.get_settings)):
    return {
        'logo': 'https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg',
        'title': 'Welcome',
        'description': 'Hello'
    }
