from pony import orm
from pydantic import BaseModel
from app.db import db


class Transaction(db.Entity):
    hash = orm.PrimaryKey(str)
    creator = orm.Required('Node')
    created = orm.Required(int)
    block = orm.Required('Block')


class TransactionOut(BaseModel):
    hash: str
    creator: str
    created: int
