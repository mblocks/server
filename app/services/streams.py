# -*- coding: utf-8 -*-
import json
from app.db.session import redis_client

redis_keys_streams = 'streams:{}'
       
def init(streams):
    pipe = redis_client.pipeline()
    for item in streams:
        item_key = redis_keys_streams.format(item)
        if not redis_client.exists(item_key):
            pipe.xgroup_create(item_key, 'all', mkstream=True)
            pipe.xgroup_create(item_key, item, mkstream=True)
    pipe.execute()
    pipe.reset()

def append(stream, dispatch, payload={}):
    pipe = redis_client.pipeline()
    if isinstance(payload,list):
        for item in payload:
            pipe.xadd(redis_keys_streams.format(stream), { "dispatch": dispatch, "payload": json.dumps(item) })
    else:
        pipe.xadd(redis_keys_streams.format(stream), { "dispatch": dispatch, "payload": json.dumps(payload) })
    pipe.execute()
    pipe.reset()

def done(consumer_group, stream, id):
    redis_client.xack(redis_keys_streams.format(stream), consumer_group, id)

def read(consumer_group, consumer, is_deliver=True, count=10, block=None):
    res = list()
    after_id = 0 if is_deliver else '>'
    streams_keys = redis_client.keys(redis_keys_streams.format('*'))
    if len(streams_keys) == 0:
        return res

    entries = redis_client.xreadgroup(consumer_group, consumer, { i : after_id for i in streams_keys }, count=count, block=block)
    if entries is None:
        return res
        
    for (name, data) in entries:
        for (entry_id, values) in data:
            res.append({'id':entry_id, 'consumer_group':consumer_group, 'stream':name.split(':')[1], 'dispatch':values.get('dispatch'), 'payload':json.loads(values.get('payload'))})
    return res

