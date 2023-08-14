from pony import orm
from pony.orm import db_session
from polydash.db import db
from polydash.model import GetOrInsertMixin


class PlaguedTransactionFound(db.Entity):
    tx_hash = orm.PrimaryKey(str)
    signer = orm.Required(str)
    nonce = orm.Required(int)
    miner_fee_block = orm.Required(str)
    miner_fee_pool = orm.Optional(str)
    block = orm.Required("PlaguedBlock")


class PlaguedTransactionMissing(db.Entity):
    tx_hash = orm.PrimaryKey(str)
    signer = orm.Required(str)
    nonce = orm.Required(int)
    miner_fee_block = orm.Required(str)
    block = orm.Required("PlaguedBlock")


class PlaguedBlock(db.Entity):
    number = orm.PrimaryKey(int)
    hash = orm.Required(str)
    violations = orm.Optional(str)  # injections, censoring, reordering
    tx_missing = orm.Set(PlaguedTransactionMissing)
    tx_found = orm.Set(PlaguedTransactionFound)
    last_violation = orm.Optional(int)
    violation_severity = orm.Optional(int)

    @classmethod
    @db_session
    def add_test_plagued_block(
        cls, block_number, hash, violations, last_violation, violation_severity
    ):
        plagued_block = cls.get(number=block_number) or cls(
            number=block_number,
            hash=hash,
            violations=violations,
            last_violation=last_violation,
            violation_severity=violation_severity,
        )
        # Add plagued block
        return plagued_block


class TransactionFetched(db.Entity):
    _table_ = "tx_fetched"
    id = orm.PrimaryKey(int, auto=True)
    tx_hash = orm.Optional(str)
    tx_fee = orm.Optional(str)
    gas_fee_cap = orm.Optional(str)
    gas_tip_cap = orm.Optional(str)
    tx_first_seen = orm.Optional(int)
    receiver = orm.Optional(str)
    signer = orm.Optional(str)
    nonce = orm.Optional(str)


class PlaguedNode(db.Entity, GetOrInsertMixin):
    pubkey = orm.PrimaryKey(str)
    outliers = orm.Optional(int, default=0)
