import logging
import time
import requests
from pathlib import Path
from app.db.session import SessionLocal
from app.db import crud
from app.services import docker
from app.config import get_settings


settings = get_settings()
container_name_prefix = settings.CONTAINER_NAME_PREFIX
network = settings.CONTAINER_NETWORK
db = SessionLocal()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if docker.get_network(network) is None:
    docker.create_network(network, subnet='172.16.0.0/16', iprange='172.16.0.0/24', gateway='172.16.0.254')

server = crud.app.get(db, id=1)
for item in server.services:
    if item.name != 'main':
        continue
    server_main = item # find server main service

if not server_main.container_id:
    """
    When server first boot, Server main container_id is empty.
    Rename it, Join network.
    """
    server_main_container = docker.get_container(image='mblocks/server')
    server_main.ip = '172.16.0.1'
    server_main.container_id = server_main_container.id
    server_main.volumes = [{'name':item_volume.split(':')[0],'value':item_volume.split(':')[1]} for item_volume in server_main_container.attrs['HostConfig']['Binds']]
    server.entrypoint = 'http://{}'.format(server_main.ip)
    server_main_container.rename('{}-{}-{}-{}'.format(container_name_prefix, server.name, server_main.name, server_main.version))
    docker.connect_network(container=server_main_container.id, network = network, ip= server_main.ip)
    db.commit()

host_volume_path = None
for item in server_main.volumes:
    if item.get('value') == '/mblocks':
        host_volume_path = item.get('name')

def deploy_stack(*, stack, prefix: str):
    # prepare images
    for item in [v.image for v in stack.services]:
        docker.get_image(item)

    # create container if not exists
    for item in stack.services:
        item_pre_container = docker.get_container(name='{}-{}-{}-{}'.format(prefix, stack.name, item.name, item.version-1))
        if item_pre_container:
            item_pre_container.rename('{}-delete-{}-{}-{}'.format(prefix, stack.name, item.name, item.version-1))
            if stack.name == 'server' and item.name == 'gateway':
                item_pre_container.stop()

        item_container_name = '{}-{}-{}-{}'.format(prefix, stack.name, item.name, item.version)
        item_container = docker.get_container(name=item_container_name)
        if item_container:
            item_container.status == 'exited' and item_container.start()
        else:
            item_image = docker.get_image(item.image)
            item_config = {
                'network': network,
                'aliases': ['{}-{}'.format(stack.name, item.name)],
                'environment':{item_env.get('name'):item_env.get('value') for item_env in item.environment } # translate list of object to dict
            }
            if stack.name =='server' and item.name == 'gateway':
                item_config['ports'] = {80:80}
            if len(item.volumes) > 0:
                item_config['volumes'] = { item_volume.get('name'):item_volume.get('value') for item_volume in item.volumes}
            elif host_volume_path and item_image.attrs['Config']['Volumes']:
                for item_volume in item_image.attrs['Config']['Volumes'].keys():
                    Path('/mblocks/{}/{}{}'.format(stack.name, item.name,item_volume)).mkdir(parents=True, exist_ok=True)
                item_config['volumes'] = { '{}/{}/{}{}'.format(host_volume_path, stack.name, item.name, item_volume):item_volume for item_volume in item_image.attrs['Config']['Volumes'].keys() }

            item_container = docker.create_container(item.image, name=item_container_name, config=item_config)
            item.ip = item_container.attrs['NetworkSettings']['Networks'][network]['IPAddress']
            item.container_id = item_container.id
            if item.name == 'main':
                stack.entrypoint = 'http://{}'.format(item.ip)
    
    return {'name':stack.name,'url':stack.entrypoint,'routes':[{'paths':[stack.path]}]}


def refresh_apps(apps):
    gateway_services = []
    for app in apps:
        gateway_services.append(deploy_stack(stack=app,prefix=container_name_prefix))
    db.commit()
    
    kong_config = {
        "_format_version": "2.1",
        "_transform": True,
        "services":gateway_services,
        "plugins":[
            {
            "name":"redis-auth",
            "config":{
                        "hide_credentials": True,
                        "redis_host": 'server-redis',
                        "redis_key_prefix": "redis-auth:",
                        "consumer_keys": ["id", "third", "third_user_id", "third_user_name","is_admin"],
                        "anonymous": True,
                        "anonymous_paths": ["/welcome"]
            }
        }
        ]
    }

    time.sleep(3)
    requests.post(('http://server-gateway:8001/config'), json=kong_config)
    docker.remove_container({'name': '{}-delete-'.format(container_name_prefix)})


def main() -> None:
    logger.info("Creating initial services")
    apps = crud.app.get_multi(db=db,search={})
    refresh_apps(apps)
    logger.info("Initial services created")


if __name__ == "__main__":
    main()
