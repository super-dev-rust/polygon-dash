from pony import orm
from pony.orm import db_session, desc, composite_key, PrimaryKey, select, distinct
from pony.utils import coalesce

from polydash.db import db


class MinerRisk(db.Entity):
    decay_coefficient = 0.9
    default_risk = 1000

    seq = orm.PrimaryKey(int, auto=True)
    miner = orm.Required(str, index=True)
    risk = orm.Required(float, index=True)

    @classmethod
    @db_session
    def add_datapoint(cls, miner, num_risk_events):
        last_point = cls.select(miner=miner).order_by(desc(cls.seq)).first()
        previous_risk = last_point.risk if last_point else cls.default_risk
        risk = previous_risk * cls.decay_coefficient + num_risk_events
        return cls(miner=miner, risk=risk)

    @classmethod
    @db_session
    def select_latest_risks(cls):
        miners = select(m.miner for m in cls)
        return [cls.select(miner=m).order_by(desc(cls.seq)).first() for m in miners]
