from typing import List

from pony import orm
from pydantic import BaseModel, validator

from polydash.common.db import db


class TransactionOut(BaseModel):
    hash: str
    creator: str
    block: int


class AuxiliaryData(db.Entity):
    key = orm.PrimaryKey(str)
    value = orm.Optional(str)


class Transaction(db.Entity):
    _table_ = "transaction"
    hash = orm.PrimaryKey(str)
    creator = orm.Optional(str)
    block = orm.Required("Block")

    # Cardano - specific
    first_seen_ts = orm.Optional(int, size=64)
    finalized_ts = orm.Optional(int, size=64)


class Block(db.Entity):
    number = orm.PrimaryKey(int)
    hash = orm.Required(str, unique=True)
    validated_by = orm.Required(str)
    transactions = orm.Set(Transaction)
    timestamp = orm.Required(int, size=64)


class BlockInDB(BaseModel):
    number: int
    hash: str
    validated_by: str
    timestamp: int
    transactions: List[TransactionOut]

    @validator("transactions", pre=True, allow_reuse=True)
    def pony_set_to_list(cls, values):
        return [v.to_dict() for v in values]

    class Config:
        orm_mode = True
