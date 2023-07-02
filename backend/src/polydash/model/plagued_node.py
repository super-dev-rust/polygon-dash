from pony import orm
from polydash.db import db_p2p

class PlaguedBlock(db_p2p.Entity):
    hash = orm.PrimaryKey(str)
    produced = orm.Required(str)
    tx_missing = orm.Required(int)
    tx_total = orm.Required(int)
    tx_reordered = orm.Required(int)

# class TransactionSummary(db_p2p.Entity):
#     _table_ = 'tx_summary'
#     id = orm.PrimaryKey(int)
#     tx_hash = orm.Optional(str)
#     peer_id = orm.Optional(str)
#     tx_first_seen = orm.Optional(int)
    

class TransactionFetched(db_p2p.Entity):
    _table_ = 'tx_fetched'
    id = orm.PrimaryKey(int)
    tx_hash = orm.Optional(str)
    tx_fee = orm.Optional(str)
    gas_fee_cap = orm.Optional(str)
    gas_tip_cap = orm.Optional(str)
    tx_first_seen = orm.Optional(int)
    receiver = orm.Optional(str)
    signer = orm.Optional(str)
    nonce = orm.Optional(str)