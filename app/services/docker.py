import docker
from docker.types import Mount

#client = docker.DockerClient(base_url='unix://var/run/docker.sock')
client = docker.from_env()

def get_network(name):
    try:
        return client.networks.get(name)
    except docker.errors.NotFound:
        return None

def create_network(name, *, subnet, iprange, gateway, aux_addresses={}):
    ipam_pool = docker.types.IPAMPool(
        subnet=subnet,
        iprange=iprange,
        gateway=gateway,
        aux_addresses=aux_addresses # exclude some ip has allocated
    )
    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
    client.api.create_network(name,ipam=ipam_config)

def connect_network(*, container, network, ip=None):
    client.api.connect_container_to_network(container,network,ipv4_address=ip)
    if ip is None:
        return get_container(name=container)

def get_container(*, name = None, image = None):
    if name:
        try:
            return client.containers.get(name)
        except docker.errors.NotFound:
            return None
    elif image:
        find_containers = client.containers.list(filters={'ancestor': image, 'status':'running'})
        if len(find_containers) == 0:
            return None
        return find_containers[0]
    return None

def create_container(image,*,name=None,config={}):
    settings = {}
    for item in ['environment']:
        if config.get(item):
            settings[item] = config.get(item)
    
    port_bindings = {}
    mounts = []
    network_config = {}
    if config.get('ports'):
        #settings['ports'] = list(config.get('ports').values())
        settings['ports'] = [80]
        port_bindings = config.get('ports')
    if config.get('volumes'):
        for source,target in config.get('volumes').items():
            mounts.append(Mount(target=target,source=source,type="bind"))
    if config.get('aliases') and config.get('network'):
        network_config[config.get('network')] = client.api.create_endpoint_config(aliases=config.get('aliases'))
        settings['networking_config'] = client.api.create_networking_config(network_config)
    settings['host_config'] = client.api.create_host_config(port_bindings=port_bindings,mounts=mounts)
    print(settings)
    container_id = client.api.create_container(image,name=name,detach=True,**settings)
    client.api.start(container=container_id)
    return get_container(name=container_id)

def remove_container(filters):
    for item in client.containers.list(all=True, filters=filters):
       item.remove(force=True)

def get_image(name):
    try:
        return client.images.get(name)
    except docker.errors.ImageNotFound:
        for line in client.api.pull(name, stream=True, decode=True):
            print(line)
        return client.images.get(name)

