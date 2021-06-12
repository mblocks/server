from typing import Optional, List
from pydantic import BaseModel
from .user import Userinfo


class Welcome(BaseModel):
    logo: Optional[str] = None
    title: Optional[str] = None
    userinfo: Optional[Userinfo] = None
