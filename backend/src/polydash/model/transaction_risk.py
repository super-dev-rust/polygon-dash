import enum

from pony import orm
from pydantic import BaseModel
from polydash.db import db
from typing import Optional


class RiskType(enum.Enum):
    NO_RISK = 0
    RISK_TOO_FAST = 1
    RISK_TOO_SLOW = 2
    RISK_INJECTION = 3


class TransactionRisk(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    hash = orm.Required(str)
    risk = orm.Optional(int)
    live_time = orm.Required(int)
    global_mean = orm.Required(float)
    global_variance = orm.Required(float)
    global_counted_txs = orm.Required(int)


class TransactionRiskOut(BaseModel):
    id: int
    hash: str
    risk: Optional[int]
    live_time: int
    global_mean: float
    global_variance: float
    global_counted_txs: int

    class Config:
        orm_mode = True
