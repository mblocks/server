# -*- coding: utf-8 -*-
import secrets
import time
import json
from passlib.context import CryptContext
from app.db.session import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_random_apikey(user) -> str:
    apikey = secrets.token_hex()
    redis_key_prefix = 'redis-auth'
    user_dict = {
        'id': user.id,
        'display_name': user.display_name
    }
    pipe = redis_client.pipeline()
    pipe.zadd('{}:sessions'.format(redis_key_prefix), {apikey: user.id})
    pipe.zadd('{}:users:{}:sessions'.format(redis_key_prefix, user.id),{apikey:time.time()})
    pipe.set('{}:users:{}'.format(redis_key_prefix, user.id), json.dumps(user_dict))
    pipe.execute()
    pipe.reset()
    return apikey


def sync_authorized(*, user_id, payload=None):
    """
    sync user authorized data to redis
    """
    if payload:
        pipe = redis_client.pipeline()
        for item_app in payload.apps:
            pipe.delete('apps:{}:users:{}:roles'.format(item_app.id, user_id)) # del key of user roles
            if len(item_app.roles) == 0:
                pipe.srem('apps:{}:users'.format(item_app.id), user_id) # remove user from key of app users
                pipe.srem('users:{}:apps'.format(user_id), item_app.id) # remove app from key of user apps
                continue
            pipe.sadd('apps:{}:users'.format(item_app.id), user_id)
            pipe.sadd('users:{}:apps'.format(user_id), item_app.id)
            for item_role in item_app.roles:
                pipe.sadd('apps:{}:users:{}:roles'.format(item_app.id, user_id), item_role.id)
        pipe.execute()
        pipe.reset()
    else:
        apps = redis_client.smembers('users:{}:apps'.format(user_id))
        pipe = redis_client.pipeline()
        for item in apps:
            pipe.srem('apps:{}:users'.format(item), user_id)
            pipe.delete('apps:{}:users:{}:roles'.format(item, user_id))
            pipe.delete('users:{}:apps'.format(user_id))
    
        pipe.execute()
        pipe.reset()

def is_authorized(*, user_id,app_id):
    return redis_client.sismember('apps:{}:users'.format(app_id), user_id)


def get_authorized(*, user_id, app_id):
    apps = [app_id] if not isinstance(app_id, list) else app_id
    pipe = redis_client.pipeline()
    for item in apps:
        pipe.smembers('apps:{}:users:{}:roles'.format(item, user_id))
    roles = pipe.execute()
    pipe.reset()
    unique_roles = {'2','4','6'}
    for item in roles:
        unique_roles = unique_roles | item
    
    res = {}
    for item in redis_client.mget(keys=['roles:{}'.format(item) for item in list(unique_roles)]):
        if item is None:
            continue
        item_dict = json.loads(item)
        #print(item_dict)
        if not res.get(item_dict['app_id']):
            res[item_dict['app_id']] = {'id':item_dict['app_id'],'name':item_dict['app_name'],'auth':{}}
        #res[item_dict['app_id']]['auth']
        for item_fun,item_limit in json.loads(item_dict.get('auth')).items():
            if not res[item_dict['app_id']]['auth'].get(item_fun):
                res[item_dict['app_id']]['auth'][item_fun]=[]
            res[item_dict['app_id']]['auth'][item_fun].append(item_limit)
    return res
    #print(json.loads(redis_client.get('roles:4')))

def sync_role(app, role):
    print(app,role)
    redis_client.set('roles:{}'.format(role.id), json.dumps({
        'app_id':app.id,
        'app_name':app.name,
        'role_id': role.id,
        'auth': role.auth
    }))