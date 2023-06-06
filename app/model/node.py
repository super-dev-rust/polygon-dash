from pony import orm
from app.model.transaction import Transaction, TransactionOut
from pydantic import BaseModel, validator
from typing import List
from app.db import db


class Node(db.Entity):
    pubkey = orm.PrimaryKey(str)
    transactions = orm.Set(Transaction)


class NodeInDB(BaseModel):
    pubkey: str
    transactions: List[TransactionOut]

    @validator('transactions', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, values):
        return [v.to_dict() for v in values]

    class Config:
        orm_mode = True
