from pony import orm

from polydash.db import db


class BlockP2P(db.Entity):
    _table_ = "block_fetched"
    id = orm.PrimaryKey(int, auto=True)
    block_hash = orm.Required(str, index=True)
    block_number = orm.Optional(int)
    first_seen_ts = orm.Optional(int)
    peer = orm.Optional(str)
    peer_remote_addr = orm.Optional(str)
    peer_local_addr = orm.Optional(str)

    @classmethod
    def get_first_by_hash(cls, block_hash):
        return cls.select().where(block_hash=block_hash).order_by(
            cls.first_seen_ts).first()
