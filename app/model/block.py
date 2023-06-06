from pony import orm
from pydantic import BaseModel, validator
from typing import List
from app.db import db
from app.model.transaction import Transaction, TransactionOut


class Block(db.Entity):
    number = orm.PrimaryKey(int)
    hash = orm.Required(str, unique=True)
    transactions = orm.Set(Transaction)


class BlockInDB(BaseModel):
    number: int
    hash: str
    transactions: List[TransactionOut]

    @validator('transactions', pre=True, allow_reuse=True)
    def pony_set_to_list(cls, values):
        return [v.to_dict() for v in values]

    class Config:
        orm_mode = True
