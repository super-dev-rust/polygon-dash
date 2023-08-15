from pony import orm
from pydantic import BaseModel
from polydash.db import db


class NodeRisk(db.Entity):
    pubkey = orm.PrimaryKey(str)
    too_fast_txs = orm.Required(int)
    too_slow_txs = orm.Required(int)


class NodeRiskInDB(BaseModel):
    pubkey: str
    too_fast_txs: int
    too_slow_txs: int

    class Config:
        orm_mode = True
