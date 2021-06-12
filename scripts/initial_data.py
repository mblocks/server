import logging
import docker
from app import schemas
from app.db.session import SessionLocal
from app.db import crud


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client = docker.from_env()


def init() -> None:
    db = SessionLocal()
    for item in client.containers.list(filters={'ancestor': 'mblocks/server'}):
        network = list(item.attrs['NetworkSettings']['Networks'].keys())[0]
        server_ip = item.attrs['NetworkSettings']['Networks'][network]['IPAddress']

    if crud.app.count(db, search={}) == 0:
        crud.app.create(db=db, obj_in=schemas.AppCreate.parse_obj({
            'name': 'server',
            'title': 'server',
            'path': '/',
            'entrypoint': 'http://{}'.format(server_ip),
            'services': [
                            {   
                                'name': 'main',
                                'title': 'server',
                                'image': 'mblocks/server',
                            },
                            {   
                                'name': 'redis',
                                'title': 'redis',
                                'image': 'redis:alpine',
                            },
                            {   
                                'name': 'gateway',
                                'title': 'gateway-title',
                                'image': 'mblocks/gateway',
                                'environment': [
                                        {'name': 'KONG_DATABASE', 'value': 'off'},
                                        {'name': 'KONG_PROXY_ACCESS_LOG', 'value': '/dev/stdout'},
                                        {'name': 'KONG_PROXY_ERROR_LOG', 'value': '/dev/stdout'},
                                        {'name': 'KONG_ADMIN_ACCESS_LOG', 'value': '/dev/stdout'},
                                        {'name': 'KONG_ADMIN_ERROR_LOG', 'value': '/dev/stdout'},
                                        {'name': 'KONG_ADMIN_LISTEN', 'value': '0.0.0.0:8001'},
                                        {'name': 'KONG_PLUGINS', 'value': 'bundled,redis-auth'},
                                ]
                            }
                        ]
        }))


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()


