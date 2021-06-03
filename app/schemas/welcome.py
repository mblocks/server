from typing import Optional, List
from pydantic import BaseModel


class Userinfo(BaseModel):
    display_name: Optional[str] = None


class Welcome(BaseModel):
    logo: Optional[str] = None
    title: Optional[str] = None
    userinfo: Optional[Userinfo] = None
