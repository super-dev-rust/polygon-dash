from typing import Optional

from pony import orm
from pydantic import BaseModel

from polydash.db import db


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
