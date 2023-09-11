from typing import Optional

from pony import orm
from pony.orm import db_session
from pydantic import BaseModel

from polydash.common.db import GetOrInsertMixin, db


class MinerRiskHistory(db.Entity):
    seq = orm.PrimaryKey(int, auto=True)
    pubkey = orm.Required(str, index=True)
    block_number = orm.Required(int, index=True)
    numblocks = orm.Required(int, index=True)
    risk = orm.Required(float, index=True)


class MinerRisk(db.Entity):
    pubkey = orm.PrimaryKey(str)
    block_number = orm.Optional(int, index=True)
    numblocks = orm.Optional(int, default=0, index=True)
    risk = orm.Optional(float, default=0.0, index=True)

    @classmethod
    @db_session
    def add_datapoint_new(cls, pubkey, new_score, block_number):
        datapoint = cls.get(pubkey=pubkey) or cls(pubkey=pubkey)
        datapoint.risk = new_score
        datapoint.numblocks += 1
        datapoint.block_number = block_number
        # Add historical record
        MinerRiskHistory(
            pubkey=pubkey,
            block_number=block_number,
            risk=datapoint.risk,
            numblocks=datapoint.numblocks,
        )
        return datapoint


class NodeStats(db.Entity, GetOrInsertMixin):
    pubkey = orm.PrimaryKey(str)
    num_outliers = orm.Required(int, default=0)
    num_injections = orm.Optional(int, default=0)
    num_txs = orm.Optional(int, default=0)


class BlockDelta(db.Entity):
    block_number = orm.PrimaryKey(int)
    hash = orm.Required(str, unique=True)
    pubkey = orm.Required(str)
    num_txs = orm.Required(int)
    num_injections = orm.Required(int)
    num_outliers = orm.Required(int)
    block_time = orm.Required(int, size=64)


class TransactionRisk(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    hash = orm.Required(str)
    risk = orm.Optional(int)
    live_time = orm.Required(int)


class TransactionRiskOut(BaseModel):
    id: int
    hash: str
    risk: Optional[int]
    live_time: int

    class Config:
        orm_mode = True
