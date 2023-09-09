from pony import orm
from pony.orm import PrimaryKey

from polydash.common.db import GetOrInsertMixin, db


class TransactionP2P(db.Entity, GetOrInsertMixin):
    _table_ = 'tx_summary'
    tx_hash = orm.Required(str, index=True)
    peer_id = orm.Required(str)
    PrimaryKey(tx_hash, peer_id)
    tx_first_seen = orm.Optional(int, size=64)

    @classmethod
    def get_first_by_hash(cls, tx_hash):
        return cls.select().where(tx_hash=tx_hash).order_by(
            cls.tx_first_seen).first()


class BlockP2P(db.Entity):
    _table_ = "block_fetched"
    id = orm.PrimaryKey(int, auto=True)
    block_hash = orm.Required(str, index=True)
    block_number = orm.Optional(int, size=64)
    first_seen_ts = orm.Optional(int, size=64)
    peer = orm.Optional(str)
    peer_remote_addr = orm.Optional(str)
    peer_local_addr = orm.Optional(str)

    @classmethod
    def get_first_by_hash(cls, block_hash):
        return cls.select().where(block_hash=block_hash).order_by(
            cls.first_seen_ts).first()
