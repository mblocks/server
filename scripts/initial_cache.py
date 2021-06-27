import logging
from app.db.session import SessionLocal
from app.db import crud, models, cache


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_cache():
    db = SessionLocal()
    query_apps = db.query(models.App)\
                   .filter(models.App.data_enabled==True)\
                   .all()
    query_roles = db.query(models.Role)\
                   .filter(models.Role.data_enabled==True)\
                   .all()
    query_users = db.query(models.User)\
                   .filter(models.User.data_enabled==True)\
                   .all()
    apps = {}
    for item in query_apps:
        apps[item.id] = item
    for item in query_roles:
        cache.set_role(app=apps.get(item.parent_id), role=item)
    
    cache.set_authorized(user={'id':1,'apps':[{'id':1,
                                                'name':'server',
                                                'title':'server',
                                                'roles':[]
                                                }]
                              }
                        ) # cache for first user
    for item in query_users:
        item_with_roles = crud.user.get_multi_with_roles(db, id=item.id)
        cache.set_authorized(user=item_with_roles)

    

def main() -> None:
    logger.info("Creating Cache")
    init_cache()
    logger.info("Initial cache created")


if __name__ == "__main__":
    main()
