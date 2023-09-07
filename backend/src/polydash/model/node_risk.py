from pony import orm
from polydash.db import db

from polydash.model import GetOrInsertMixin


class NodeStats(db.Entity, GetOrInsertMixin):
    pubkey = orm.PrimaryKey(str)
    num_outliers = orm.Required(int, default=0)
    num_injections = orm.Optional(int, default=0)
    num_txs = orm.Optional(int, default=0)


class BlockDelta(db.Entity):
    block_number = orm.PrimaryKey(int)
    hash = orm.Required(str, unique=True)
    pubkey = orm.Required(str)
    num_txs = orm.Required(int)
    num_injections = orm.Required(int)
    num_outliers = orm.Required(int)
    block_time = orm.Required(int)
