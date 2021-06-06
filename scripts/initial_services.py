import os
import time
import docker
import requests
from app.config import get_settings

settings = get_settings()

#client = docker.from_env()
client = docker.DockerClient(base_url='unix://var/run/docker.sock')
container_name_prefix = settings.CONTAINER_NAME_PREFIX
mock = False
plugins = []
services = {
    'gateway': {
        'image': 'mblocks/gateway',
        'settings': {
            'ports': {'80': '80','8001':'8001'},
            'environment': {
                'KONG_DATABASE': 'off',
                'KONG_PROXY_ACCESS_LOG': '/dev/stdout',
                'KONG_PROXY_ERROR_LOG': '/dev/stdout',
                'KONG_ADMIN_ACCESS_LOG': '/dev/stdout',
                'KONG_ADMIN_ERROR_LOG': '/dev/stdout',
                'KONG_ADMIN_LISTEN': '0.0.0.0:8001',
                'KONG_PLUGINS': 'bundled,redis-auth',
            }
        },
    },
    'redis': {
        'image': 'redis:alpine',
        'settings': {}
    }
}



# prepare images
for item in [v.get('image') for k,v in services.items()]:
    try:
        client.images.get(item)
    except docker.errors.ImageNotFound:
        for line in client.api.pull(item, stream=True, decode=True):
            print(line)


# get mblocks/server network
for item in client.containers.list(filters={'ancestor': 'mblocks/server'}):
    server_network = list(item.attrs['NetworkSettings']['Networks'].keys())[0]
    server_ip = item.attrs['NetworkSettings']['Networks'][server_network]['IPAddress']



# create container if not exists
for name, item in services.items():
    try:
        client.containers.get(container_name_prefix + name)
    except docker.errors.NotFound:
        client.containers.run(item.get('image'),
                              name=container_name_prefix + name,
                              detach=True,
                              network=server_network,
                              **item.get('settings')
                              )

# get mblocks's container ip adress
for item in client.containers.list(all=True, filters={'name': container_name_prefix}):
    # start exited container
    if item.status == 'exited':
        item.start()
    # get container's ip
    services[item.name.replace(container_name_prefix, '')]['ip'] = item.attrs['NetworkSettings']['Networks'][server_network]['IPAddress']


if services.get('redis'):
    with open('/etc/hosts', 'a') as f:
        print('{} redis'.format(services['redis']['ip']), file=f)  # Python 3.x




kong_config = {
    "_format_version": "2.1",
    "_transform": True,
    "services":[
        {
            "name": "server",
            "url": 'http://{}/'.format(server_ip),
            "routes": [ { "paths": ["/"] } ]
        }
    ],
    "plugins":[
        {
          "name":"redis-auth",
          "config":{
                    "hide_credentials": True,
                    "redis_host": services['redis']['ip'],
                    "redis_key_prefix": "redis-auth:",
                    "consumer_keys": ["id", "third", "third_user_id", "third_user_name","is_admin"],
                    "anonymous": True,
                    "anonymous_paths": ["/welcome"]
          }
      }
    ]
}
time.sleep(3)
print(kong_config)
resp = requests.post(('http://{}:8001/config'.format(services['gateway']['ip'])), json=kong_config)
