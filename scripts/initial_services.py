import logging
import time
import docker
import requests
from app.db.session import SessionLocal
from app.db import crud
from app.config import get_settings


settings = get_settings()
container_name_prefix = settings.CONTAINER_NAME_PREFIX
client = docker.from_env()
#client = docker.DockerClient(base_url='unix://var/run/docker.sock')
db = SessionLocal()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

network = ''
server_ip = ''
for item in client.containers.list(filters={'ancestor': 'mblocks/server'}):
    network = list(item.attrs['NetworkSettings']['Networks'].keys())[0]
    server_ip = item.attrs['NetworkSettings']['Networks'][network]['IPAddress']

if network == '':
    try:
        raise ValueError
    except ValueError:
        print("Can not find docker image mblocks/server running")

def deploy_stack(client, *, network, stack, server_ip,prefix: str):
    stack_status = {}
    # prepare images
    for item in [v.image for v in stack.services]:
        try:
            client.images.get(item)
        except docker.errors.ImageNotFound:
            for line in client.api.pull(item, stream=True, decode=True):
                print(line)

    # create container if not exists
    for item in stack.services:
        item_container_name = '{}-{}-{}'.format(prefix, stack.name, item.name)
        item_settings = {
            'ports': {'80': '80'} if stack.name =='server' and item.name == 'gateway' else {},
            'environment':{item_env.get('name'):item_env.get('value') for item_env in item.environment } # translate list of object to dict
        }

        stack_status[item.name] = {'ip':'','container_id':''}
        if item.image == 'mblocks/server':
            stack_status[item.name]['ip'] = server_ip
            continue
        
        try:
            client.containers.get(item_container_name)
        except docker.errors.NotFound:
            item_image = client.images.get(item.image)
            if item_image.attrs['Config']['Volumes']:
                for item_image_volume in item_image.attrs['Config']['Volumes'].keys():
                    item_settings['volumes'] = {'/mblocks/{}/{}{}'.format(stack.name, item.name, item_image_volume): {'bind': item_image_volume, 'mode': 'rw'}}
            client.containers.run(item.image,
                                name=item_container_name,
                                detach=True,
                                network=network,
                                hostname=item_container_name,
                                **item_settings
                                )
    
    # get stack's container ip adress
    for item in client.containers.list(all=True, filters={'name': '{}-{}-'.format(prefix, stack.name)}):
        # get container's ip
        stack_status[item.name.replace('{}-{}-'.format(prefix, stack.name), '')] = {
            'ip':item.attrs['NetworkSettings']['Networks'][network]['IPAddress'],
            'container_id':item.id
        }

    for item in stack.services:
        print(item)
        item.ip = stack_status[item.name]['ip']
        item.container_id = stack_status[item.name]['container_id']
    
    stack.entrypoint = 'http://{}'.format(stack_status['main']['ip'])
    return {'name':stack.name,'url':stack.entrypoint,'routes':[{'paths':[stack.path]}]}


def refresh_apps():
    gateway_services = []
    for app in crud.app.get_multi(db=db,search={}):
        gateway_services.append(deploy_stack(client=client,network=network,stack=app,server_ip=server_ip,prefix=container_name_prefix))
    db.commit()
    #get app server, find redis,gateway ip address
    server = crud.app.get(db=db,id=1)

    for item in server.services:
        if item.name == 'redis':
            server_redis_ip = item.ip
        if item.name == 'gateway':
            server_gateway_ip = item.ip

    # write redis ip to /etc/hosts
    with open('/etc/hosts', 'a') as f:
        print('{} redis'.format(server_redis_ip), file=f)  # Python 3.x

    kong_config = {
        "_format_version": "2.1",
        "_transform": True,
        "services":gateway_services,
        "plugins":[
            {
            "name":"redis-auth",
            "config":{
                        "hide_credentials": True,
                        "redis_host": server_redis_ip,
                        "redis_key_prefix": "redis-auth:",
                        "consumer_keys": ["id", "third", "third_user_id", "third_user_name","is_admin"],
                        "anonymous": True,
                        "anonymous_paths": ["/welcome"]
            }
        }
        ]
    }

    time.sleep(3)
    requests.post(('http://{}:8001/config'.format(server_gateway_ip)), json=kong_config)


def main() -> None:
    logger.info("Creating initial services")
    refresh_apps()
    logger.info("Initial services created")


if __name__ == "__main__":
    main()
