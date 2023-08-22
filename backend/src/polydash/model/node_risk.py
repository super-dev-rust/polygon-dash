from pony import orm
from pydantic import BaseModel
from polydash.db import db

from polydash.model import GetOrInsertMixin


class NodeRisk(db.Entity, GetOrInsertMixin):
    pubkey = orm.PrimaryKey(str)
    too_fast_txs = orm.Optional(int, default=0)
    too_slow_txs = orm.Optional(int, default=0)


class NodeRiskInDB(BaseModel):
    pubkey: str
    too_fast_txs: int
    too_slow_txs: int

    class Config:
        orm_mode = True
