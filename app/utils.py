# -*- coding: utf-8 -*-
import secrets
import time
import json
from passlib.context import CryptContext
from app.db.session import redis_client

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_random_str() -> str:
    return secrets.token_hex()
