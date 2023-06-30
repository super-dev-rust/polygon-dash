from pony import orm
from pydantic import BaseModel
from polydash.db import db


class Node(db.Entity):
    pubkey = orm.PrimaryKey(str)
    outliers = orm.Required(int)
    mean = orm.Required(float)
    variance = orm.Required(float)
    n_txs = orm.Required(int)
    last_txs = orm.Required(orm.IntArray)


class NodeInDB(BaseModel):
    pubkey: str
    outliers: int
    mean: float
    variance: float
    n_txs: int

    class Config:
        orm_mode = True
