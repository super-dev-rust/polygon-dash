import enum

from pony import orm
from tdigest import TDigest


class RiskType(enum.Enum):
    NO_RISK = 0
    RISK_TOO_FAST = 1
    RISK_TOO_SLOW = 2
    RISK_INJECTION = 3


class OutlierDetector:
    def __init__(self, TX_RISK_CLASS):
        self.tdigest = TDigest()
        self.TX_RISK = TX_RISK_CLASS

        with orm.db_session:
            # Select last 10000 transactions and update digest
            txs = self.TX_RISK.select().order_by(self.TX_RISK.id)[:10000]
            for t in txs:
                self.tdigest.update(t.live_time)

    def add_new_transaction(self, tx_live_time: int):
        self.tdigest.update(tx_live_time)

    def assess_transaction_risk(
        self, tx_finalized_time: int, tx_arrival_time: int
    ) -> RiskType:
        tx_live_time = tx_finalized_time - tx_arrival_time
        if tx_live_time < 0:
            return RiskType.RISK_TOO_FAST
        self.add_new_transaction(tx_live_time)
        if tx_live_time <= self.tdigest.percentile(1):
            return RiskType.RISK_TOO_FAST
        elif tx_live_time >= self.tdigest.percentile(99):
            return RiskType.RISK_TOO_SLOW
        else:
            return RiskType.NO_RISK
