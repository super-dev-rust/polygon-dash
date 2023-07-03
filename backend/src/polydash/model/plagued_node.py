from pony import orm
from polydash.db import db_p2p, db

class PlaguedTransactionFound(db.Entity):
    tx_hash = orm.PrimaryKey(str)
    signer = orm.Required(str)
    nonce = orm.Required(int)
    miner_fee_block = orm.Required(str)
    miner_fee_pool = orm.Optional(str)
    block = orm.Required('PlaguedBlock')
    
    
class PlaguedTransactionMissing(db.Entity):
    tx_hash = orm.PrimaryKey(str)
    signer = orm.Required(str)
    nonce = orm.Required(int)
    miner_fee_block = orm.Required(str)
    block = orm.Required('PlaguedBlock')


class PlaguedBlock(db.Entity):
    number = orm.PrimaryKey(int)
    hash = orm.Required(str)
    violations = orm.Optional(str) #injections, censoring, reordering
    tx_missing = orm.Set(PlaguedTransactionMissing)
    tx_found = orm.Set(PlaguedTransactionFound)
    last_violation = orm.Optional(int)
    violation_severity = orm.Optional(int)

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
    
class PlaguedNode(db.Entity):
    pubkey = orm.PrimaryKey(str)
    outliers = orm.Required(int)