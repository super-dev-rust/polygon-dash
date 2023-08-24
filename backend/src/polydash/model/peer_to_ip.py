from pony import orm
from pydantic import BaseModel
from polydash.db import db
from polydash.model import GetOrInsertMixin


class PeerToIP(db.Entity, GetOrInsertMixin):
    id = orm.PrimaryKey(int, auto=True)
    peer_id = orm.Required(str)
    ip = orm.Required(str)


class PeerToIPInDB(BaseModel):
    id: int
    peer_id: str
    ip: str

    class Config:
        orm_mode = True
