from typing import List

from pony import orm
from pony.orm import PrimaryKey
from pydantic import BaseModel

from polydash.common.db import db, GetOrInsertMixin


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


class DeanonNodeByTx(db.Entity, GetOrInsertMixin):
    id = orm.PrimaryKey(int, auto=True)
    signer_key = orm.Required(str)
    peer_id = orm.Required(str)
    confidence = orm.Required(int, default=0)


class DeanonNodeByTxInDB(BaseModel):
    id: int
    signer_key: str
    peer_id: str
    confidence: int

    class Config:
        orm_mode = True


class DeanonNodeByTxWithIP(BaseModel):
    node: DeanonNodeByTxInDB
    ips: List[str]


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
