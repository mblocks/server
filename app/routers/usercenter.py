# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from app import config

router = APIRouter()

@router.get("/whoami")
async def get_current_user(settings: config.Settings = Depends(config.get_settings)):
    return {
        'logo': 'https://gw.alipayobjects.com/zos/rmsportal/KDpgvguMpGfqaHPjicRK.svg',
        'title': 'Welcome',
        'description': 'Hello2',
        'userinfo':{
            'user_name':'myname'
        }
    }
