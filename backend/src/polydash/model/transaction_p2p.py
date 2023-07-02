from pony import orm
from polydash.db import db_p2p


class TransactionP2P(db_p2p.Entity):
    _table_ = 'tx_summary'
    id = orm.PrimaryKey(int)
    tx_hash = orm.Optional(str)
    peer_id = orm.Optional(str)
    tx_first_seen = orm.Optional(int)
