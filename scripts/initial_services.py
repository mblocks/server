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
network = 'mblocks'

try:
    client.networks.get(network)
except docker.errors.NotFound:
    ipam_pool = docker.types.IPAMPool(
        subnet='172.16.0.0/16',
        iprange='172.16.0.0/24',
        gateway='172.16.0.254',
        aux_addresses={
            'server-main':'172.16.0.1'
        } # exclude some ip has allocated
    )
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
    client.api.create_network(network,ipam=ipam_config)

server_ip = '172.16.0.1'
server_exists_network = False
for item in client.containers.list(filters={'ancestor': 'mblocks/server'}):
    server_id = item.id
    if item.name != '{}-{}-{}'.format(container_name_prefix, 'server', 'main'):
        item.rename('{}-{}-{}'.format(container_name_prefix, 'server', 'main'))
    if network in item.attrs['NetworkSettings']['Networks']:
        server_exists_network = True

if not server_exists_network:
    client.api.connect_container_to_network(server_id,network,ipv4_address=server_ip)


def deploy_stack(client, *, network, stack,prefix: str):
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
        try:
            item_container = client.containers.get(item_container_name)
            if item_container.status == 'exited':
                item_container.start()
        except docker.errors.NotFound:
            item_image = client.images.get(item.image)
            item_settings = {
                'ports':[80] if stack.name =='server' and item.name == 'gateway' else [],
                'host_config':client.api.create_host_config(port_bindings={80:80}) if stack.name =='server' and item.name == 'gateway' else {},
                'environment':{item_env.get('name'):item_env.get('value') for item_env in item.environment } # translate list of object to dict
            }
            if item_image.attrs['Config']['Volumes']:
                for item_image_volume in item_image.attrs['Config']['Volumes'].keys():
                    item_settings['volumes'] = {'/mblocks/{}/{}{}'.format(stack.name, item.name, item_image_volume): {'bind': item_image_volume, 'mode': 'rw'}}

            item_endpoint_config =  client.api.create_endpoint_config(aliases=['{}-{}'.format(stack.name, item.name)])
            item_network_config = { network:item_endpoint_config }
            container_id  = client.api.create_container(item.image,
                                                        name=item_container_name,
                                                        detach=True,
                                                        networking_config = client.api.create_networking_config(item_network_config),
                                                        **item_settings
                                                        )
            client.api.start(container=container_id)

    # get stack's container ip adress
    for item in client.containers.list(all=True, filters={'name': '{}-{}-'.format(prefix, stack.name)}):
        # get container's ip
        stack_status[item.name.replace('{}-{}-'.format(prefix, stack.name), '')] = {
            'ip':item.attrs['NetworkSettings']['Networks'][network]['IPAddress'],
            'container_id':item.id
        }

    for item in stack.services:
        item.ip = stack_status[item.name]['ip']
        item.container_id = stack_status[item.name]['container_id']
    
    stack.entrypoint = 'http://{}'.format(stack_status['main']['ip'])
    return {'name':stack.name,'url':stack.entrypoint,'routes':[{'paths':[stack.path]}]}


def refresh_apps():
    gateway_services = []
    for app in crud.app.get_multi(db=db,search={}):
        gateway_services.append(deploy_stack(client=client,network=network,stack=app,prefix=container_name_prefix))
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


def main() -> None:
    logger.info("Creating initial services")
    refresh_apps()
    logger.info("Initial services created")


if __name__ == "__main__":
    main()
