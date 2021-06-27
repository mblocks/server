# -*- coding: utf-8 -*-
import secrets
import time
import json
from app import schemas, utils
from .session import redis_client

perfix = 'redis-auth'
key_sessions = '{}:sessions'.format(perfix)
key_users = '{}:users:{}'.format(perfix,'{}')
key_users_sessions = '{}:users:{}:sessions'.format(perfix,'{}')
key_users_authorized = '{}:users:{}:authorized'.format(perfix,'{}')
key_roles = 'roles:{}'

def generate_apikey(current_user) -> str:
    apikey = utils.generate_random_str()
    pipe = redis_client.pipeline()
    pipe.zadd(key_sessions, {apikey: current_user.id})
    pipe.zadd(key_users_sessions.format(current_user.id),{apikey:time.time()})
    pipe.set(key_users.format(current_user.id), json.dumps({
        'id': current_user.id,
        'third': current_user.third if hasattr(current_user,'third')  else '',
        'third_user_id': current_user.third_user_id if hasattr(current_user,'third_user_id') else '',
        'third_user_name': current_user.third_user_name if hasattr(current_user,'third_user_name') else '',
    }))
    pipe.execute()
    pipe.reset()
    return apikey

def set_authorized(user):
    redis_client.set(key_users_authorized.format(user.get('id')), json.dumps({item.get('id'):item for item in user.get('apps')}))

def del_authorized(user_id):
    redis_client.delete(key_users_authorized.format(user_id))

def get_authorized(user_id, lite=True):
    authorized = redis_client.get(key_users_authorized.format(user_id))
    if authorized is None:
        return {}
    if lite == True:
        return json.loads(authorized)
        
    roles = []
    for item_app in json.loads(authorized).values():
        for item_role in item_app.get('roles'):
            roles.append('roles:{}'.format(item_role.get('id')))

    res = {}
    for item in json.loads('[{}]'.format(','.join([i for i in redis_client.mget(keys=roles) if i]))):
        """
        get redis and remove not exists role to json string
        """
        if not res.get(item['app_id']):
            res[item['app_id']] = {'id':item['app_id'],'name':item['app_name'],'auth':{}}
        for item_fun,item_limit in json.loads(item.get('auth')).items():
            if not res[item['app_id']]['auth'].get(item_fun):
                res[item['app_id']]['auth'][item_fun]=[]
            res[item['app_id']]['auth'][item_fun].append(item_limit)
    return res
    
def set_role(app, role):
    redis_client.set(key_roles.format(role.id), json.dumps({
        'app_id':app.id,
        'app_name':app.name,
        'role_id': role.id,
        'auth': role.auth
    }))

def del_role(role_id):
    redis_client.delete(key_roles.format(role_id))
