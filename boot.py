import docker
import requests
import time


#client = docker.from_env()
client = docker.DockerClient(base_url='unix://var/run/docker.sock')
mock = True
plugins = []
services = []

mblocks_network = 'mblocks'
mblocks_containers = {
    'gateway':{
        'image':'mblocks/gateway',
        'settings':{
            'ports':{'80':'80','8001':'8001'},
            'environment': {
                            'KONG_DATABASE':'off',
                            'KONG_PROXY_ACCESS_LOG':'/dev/stdout',
                            'KONG_PROXY_ERROR_LOG':'/dev/stdout',
                            'KONG_ADMIN_ACCESS_LOG':'/dev/stdout',
                            'KONG_ADMIN_ERROR_LOG':'/dev/stdout',
                            'KONG_ADMIN_LISTEN':'0.0.0.0:8001',
                            'KONG_PLUGINS':'bundled,redis-auth',
                           }
        },
    },
    'redis':{
        'image':'redis:alpine',
        'settings':{}
    },
    'mock':{
        'image':'mock-server',
        'settings':{},
        'service':{
            'endpoint':'http://{ip}:8000/api/',
            'paths': ['/']
        },
    }
}

# genrerate kong declare config


if mock:
    mblocks_containers['mock'] = {
                                    'image':'mock-server',
                                    'settings':{},
                                    'service':{
                                                'endpoint':'http://{ip}:8000/api/',
                                                'paths': ['/']
                                            },
                                }
else:
    plugins.append({
        'name':'redis-auth',
        'config': {
            'hide_credentials': True,
            'redis_host': mblocks_containers['redis']['ip'],
            'redis_key_prefix': 'redis-auth:',
            'consumer_keys':['user_id','third','third_user_id','third_user_name']
        }
    })


# create a network named mblocks if not exists
if len([i for i in client.networks.list() if i.name==mblocks_network]) == 0:
    client.networks.create(mblocks_network)


# create container if not exists
for name, item in mblocks_containers.items():
    try:
        client.containers.get('mblocks_{}'.format(name))
    except docker.errors.NotFound:
        client.containers.run(item.get('image'),
                                              name='mblocks_{}'.format(name),
                                              detach=True,
                                              network=mblocks_network,
                                              **item.get('settings')
                                            )
        

# get mblocks's container ip adress
for item in client.containers.list(all=True,filters={'name':'mblocks_'}):
    # start exited container
    if item.status == 'exited':
        item.start()
    # get container's ip
    mblocks_containers[item.name.replace('mblocks_','')]['ip'] = item.attrs['NetworkSettings']['Networks']['mblocks']['IPAddress']







for name, item in mblocks_containers.items():
    service =  item.get('service')
    if service:
        services.append({
            'name':name,
            'url':item.get('service').get('endpoint').format(ip=item.get('ip')),
            'routes':[{
                'paths':item.get('service').get('paths')
            }]
        })

time.sleep(10)
resp = requests.post('http://172.20.0.2:8001/config', json={
  "_format_version": "2.1",
  "_transform": True,
  "services": services,
  "plugins": plugins
})

print(resp.text)
