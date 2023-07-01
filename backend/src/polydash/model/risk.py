from pony import orm
from pony.orm import db_session

from polydash.db import db


class MinerRiskHistory(db.Entity):
    seq = orm.PrimaryKey(int, auto=True)
    pubkey = orm.Required(str, index=True)
    numblocks = orm.Required(int, index=True)
    risk = orm.Required(float, index=True)


class MinerRisk(db.Entity):
    decay_coefficient = 0.9

    pubkey = orm.PrimaryKey(str)
    numblocks = orm.Optional(int, default=0, index=True)
    risk = orm.Optional(float, default=100, index=True)

    @classmethod
    @db_session
    def add_datapoint(cls, pubkey, num_risk_events):
        datapoint = cls.get(pubkey=pubkey) or cls(pubkey=pubkey)
        datapoint.risk = datapoint.risk * cls.decay_coefficient + num_risk_events
        datapoint.numblocks += 1
        # Add historical record
        MinerRiskHistory(pubkey=pubkey, risk=datapoint.risk, numblocks=datapoint.numblocks)
        return datapoint
