from pony import orm
from pony.orm import PrimaryKey

from polydash.db import db
from polydash.model import GetOrInsertMixin


class TransactionP2P(db.Entity, GetOrInsertMixin):
    _table_ = 'tx_summary'
    tx_hash = orm.Required(str)
    peer_id = orm.Required(str)
    PrimaryKey(tx_hash, peer_id)
    tx_first_seen = orm.Optional(int)

    @classmethod
    def get_first_by_hash(cls, tx_hash):
        return cls.select().where(tx_hash=tx_hash).order_by(
            cls.tx_first_seen).first()
