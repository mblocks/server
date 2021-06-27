import logging
from app import schemas
from app.db.session import SessionLocal
from app.db import crud, models


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    db = SessionLocal()
    if crud.app.count(db, search={}) == 0:
        crud.app.create(db=db, obj_in=schemas.AppCreate.parse_obj({
            'name': 'server',
            'title': 'server',
            'path': '/',
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

        db.add(models.Role(parent_id=1,title='管理员',auth='{}'))
        db.add(models.Authorized(user_id=1,role_id=1,app_id=1)) # first user is admin
        db.commit()


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()


