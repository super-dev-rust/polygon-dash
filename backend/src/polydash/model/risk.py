from pony import orm
from pony.orm import db_session

from polydash.db import db


class MinerRiskHistory(db.Entity):
    seq = orm.PrimaryKey(int, auto=True)
    pubkey = orm.Required(str, index=True)
    block_number = orm.Required(int, index=True)
    numblocks = orm.Required(int, index=True)
    risk = orm.Required(float, index=True)


class MinerRisk(db.Entity):
    decay_coefficient = 0.9

    pubkey = orm.PrimaryKey(str)
    block_number = orm.Optional(int, index=True)
    numblocks = orm.Optional(int, default=0, index=True)
    risk = orm.Optional(float, default=100, index=True)

    @classmethod
    @db_session
    def add_datapoint(cls, pubkey, num_risk_events, block_number):
        datapoint = cls.get(pubkey=pubkey) or cls(pubkey=pubkey)
        datapoint.risk = datapoint.risk * cls.decay_coefficient + num_risk_events
        datapoint.numblocks += 1
        datapoint.block_number = block_number
        # Add historical record
        MinerRiskHistory(pubkey=pubkey, block_number=block_number, risk=datapoint.risk, numblocks=datapoint.numblocks)
        return datapoint

    @classmethod
    @db_session
    def add_datapoint_new(cls, pubkey, d_coef, num_injects, num_outliers, num_txs, block_number):
        datapoint = cls.get(pubkey=pubkey) or cls(pubkey=pubkey)
        datapoint.risk = d_coef * (0.8 * (1 - num_injects / num_txs)
                                   + 0.2 * (1 - num_outliers / num_txs))
        datapoint.numblocks += 1
        datapoint.block_number = block_number
        # Add historical record
        MinerRiskHistory(pubkey=pubkey, block_number=block_number,
                         risk=datapoint.risk, numblocks=datapoint.numblocks)
        return datapoint
