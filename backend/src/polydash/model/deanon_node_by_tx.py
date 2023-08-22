from pony import orm
from pydantic import BaseModel
from polydash.db import db
from polydash.model import GetOrInsertMixin


class DeanonNodeByTx(db.Entity, GetOrInsertMixin):
    id = orm.PrimaryKey(int, auto=True)
    signer_key = orm.Required(str)
    peer_id = orm.Required(str)
    confidence = orm.Required(int, default=0)


class DeanonNodeByTxInDB(BaseModel):
    id: int
    signer_key: str
    peer_id: str
    confidence: int

    class Config:
        orm_mode = True
