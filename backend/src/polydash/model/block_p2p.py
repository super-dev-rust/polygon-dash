from pony import orm
from polydash.db import db_p2p


class BlockP2P(db_p2p.Entity):
    _table_ = "block_fetched"
    id = orm.PrimaryKey(int)
    block_hash = orm.Optional(str)
    block_number = orm.Optional(int)
    first_seen_ts = orm.Optional(int)
    peer = orm.Optional(str)
    peer_remote_addr = orm.Optional(str)
    peer_local_addr = orm.Optional(str)
