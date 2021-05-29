from pydantic import BaseModel


class DBBase(BaseModel):
    id: int

    class Config:
        orm_mode = True
