from pony import orm
from polydash.db import db_p2p, db

class PlaguedTransaction(db.Entity):
    tx_hash = orm.PrimaryKey(str)
    signer = orm.Required(str)
    nonce = orm.Required(int)
    miner_fee = orm.Required(str)
    violations = orm.Optional(str)
    block = orm.Required('PlaguedBlock')


class PlaguedBlock(db.Entity):
    number = orm.PrimaryKey(int)
    hash = orm.Required(str)
    tx_missing_amount = orm.Required(int)
    tx_remote_total_amount = orm.Required(int)
    tx_found_amount = orm.Required(int)
    txs_found = orm.Set(PlaguedTransaction)
    # txs_missing = orm.Set(PlaguedTransaction)

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
    
