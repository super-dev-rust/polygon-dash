from pony import orm
from pony.orm import PrimaryKey
from pydantic import BaseModel
from polydash.db import db
from polydash.model import GetOrInsertMixin


class DeanonNodeByBlock(db.Entity, GetOrInsertMixin):
    signer_key = orm.Required(str)
    peer_id = orm.Required(str)
    PrimaryKey(signer_key, peer_id)
    confidence = orm.Optional(int, default=0)


class DeanonNodeByBlockInDB(BaseModel):
    signer_key: str
    peer_id: str
    confidence: int

    class Config:
        orm_mode = True
