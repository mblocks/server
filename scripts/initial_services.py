# -*- coding: utf-8 -*-
import os
import time
import requests
from pathlib import Path
from app.db.session import SessionLocal
from app.db import crud
from app.services import docker
from app.config import get_settings


def get_config(db) ->None:
    settings = get_settings()
    container_name_prefix = settings.CONTAINER_NAME_PREFIX
    network = settings.CONTAINER_NETWORK
    if docker.get_network(network) is None:
        docker.create_network(network, subnet='172.16.0.0/16', iprange='172.16.0.0/24', gateway='172.16.0.254')
    
    server = crud.app.get(db, id=1)
    for item in server.services:
        if item.name != 'main':
            continue
        server_main = item # find server main service
    
    server_main_container = docker.get_container(name=server_main.container_id)
    if server_main_container is None:
        """
        When server first boot, Server main container_id is empty.
        Rename it, Join network.
        """
        server_main_container = docker.get_container(image='mblocks/server')
        server_main_container = docker.connect_network(container=server_main_container.id, network = network)
        server_main_container.rename('{}-{}-{}-{}'.format(container_name_prefix, server.name, server_main.name, server_main.version))
        server_main.volumes = [{'name':item_volume.split(':')[0],'value':item_volume.split(':')[1]} for item_volume in server_main_container.attrs['HostConfig']['Binds']]
        server_main.ip = server_main_container.attrs['NetworkSettings']['Networks'][network]['IPAddress']
        server_main.container_id = server_main_container.id
        server_main.environment = [{'name':item,'value':os.getenv(item)} for item in settings.Environment if os.getenv(item)]
        server.entrypoint = 'http://{}'.format(server_main.ip)
        db.commit()

    host_volume_path = None
    for item in server_main.volumes:
        if item.get('value') == '/mblocks':
            host_volume_path = item.get('name')

    return {
            'network': network,
            'container_name_prefix': container_name_prefix,
            'host_volume_path': host_volume_path,
           }

def deploy_stack(*, stack, prefix: str, network: str, host_volume_path: str):
    # prepare images
    for item in [v.image for v in stack.services]:
        docker.get_image(item)

    # create container if not exists
    for item in stack.services:
        item_pre_container = docker.get_container(name='{}-{}-{}-{}'.format(prefix, stack.name, item.name, item.version-1))
        if item_pre_container:
            item_pre_container.rename('{}-delete-{}-{}-{}'.format(prefix, stack.name, item.name, item.version-1))
            if 'mblocks/gateway' in item.image:
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
            if 'mblocks/gateway' in item.image:
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
    
    return {'name':stack.name,'url':stack.entrypoint,'routes':[{'paths':[stack.path if stack.path else '/{}'.format(stack.name)]}]}


def refresh_apps():
    db = SessionLocal()
    config = get_config(db)
    apps = crud.app.get_multi(db=db,search={},order_by='id desc')
    services = []
    for app in apps:
        services.append(deploy_stack(stack=app,
                                     prefix=config.get('container_name_prefix'),
                                     network=config.get('network'),
                                     host_volume_path=config.get('host_volume_path')
                                    )
                               )
    db.commit()
    
    kong_config = {
        "_format_version": "2.1",
        "_transform": True,
        "services":services,
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
    print(kong_config)
    docker.remove_container({'name': '{}-delete-'.format(config.get('container_name_prefix'))})

def main() -> None:
    refresh_apps()


if __name__ == "__main__":
    main()
