# -*- coding: utf-8 -*-
import os
import sys
from functools import lru_cache
from pydantic import BaseSettings

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class Settings(BaseSettings):
    FASTAPI_CONFIG: str = os.getenv("FASTAPI_CONFIG", "development")
    APP_NAME: str = "Mblocks Server"
    OPENAPI_PREFIX: str = ""
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
                                            "SQLALCHEMY_DATABASE_URI",
                                            prefix + os.path.join(basedir, 'data.db')
                                            )
    SQLALCHEMY_ECHO: bool = os.getenv('SQLALCHEMY_ECHO',False)
    REDIS_HOST: str = os.getenv('REDIS_HOST','localhost')
    REDIS_PORT: int = os.getenv('REDIS_PORT',6379)
    REDIS_DB: int = os.getenv('REDIS_DB',0)

    CONTAINER_NAME_PREFIX: str = 'mblocks'
    class Config:
        case_sensitive: bool = True
        env_file: bool = ".env"


@lru_cache()
def get_settings():
    return Settings()
