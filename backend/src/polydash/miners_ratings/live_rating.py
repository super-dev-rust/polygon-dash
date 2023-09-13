import queue
import threading
import traceback

from pony import orm
from pony.orm import select

from polydash.common.log import LOGGER
from polydash.common.model import Block
from polydash.miners_ratings.model import NodeStats, BlockDelta, MinerRisk
from polydash.polygon.p2p_data.model import TransactionP2P, BlockP2P
from polydash.miners_ratings.model import TransactionRisk
from polydash.miners_ratings.injections import (
    InjectionDetector,
    INJECTION_DELAY_THRESHOLD,
)
from polydash.miners_ratings.outliers import OutlierDetector, RiskType
from polydash.miners_ratings.rating_func import activity_coef, trust_score

TransactionEventQueue = queue.Queue()


class PolygonRatingProcessor(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = LOGGER.getChild(self.__class__.__name__)
        self.outlier_detector = OutlierDetector(TransactionRisk)

    def process_transaction(
        self,
        tx_hash: str,
        tx_finalized: int,
        block_author: NodeStats,
        block_delta: BlockDelta,
    ):
        tx_arrival_time = None
        if (tx_p2p := TransactionP2P.get_first_by_hash(tx_hash)) is not None:
            tx_arrival_time = tx_p2p.tx_first_seen
        is_inject = InjectionDetector.is_transaction_injection(
            tx_finalized, tx_arrival_time
        )
        if is_inject:
            block_author.num_injections += 1
            block_delta.num_injections += 1
            tx_risk = RiskType.RISK_INJECTION
        else:
            tx_risk = self.outlier_detector.assess_transaction_risk(
                tx_finalized, tx_arrival_time
            )
            if tx_risk == RiskType.RISK_TOO_FAST:
                block_author.num_outliers += 1
                block_delta.num_outliers += 1
        # Record transaction risk
        if not tx_arrival_time:
            tx_arrival_time = tx_finalized - INJECTION_DELAY_THRESHOLD

        TransactionRisk(
            hash=tx_hash, live_time=tx_finalized - tx_arrival_time, risk=tx_risk.value
        )

    def process_block(self, block: Block):
        with orm.db_session:
            if (block_from_p2p := BlockP2P.get_first_by_hash(block.hash)) is not None:
                block_ts = block_from_p2p.first_seen_ts
            else:
                block_ts = block.timestamp * 1000

            if BlockDelta.get(block_number=block.number) is not None:
                # Block already processed
                return

            num_txs = len(block.transactions)
            block_delta = BlockDelta(
                block_number=block.number,
                hash=block.hash,
                pubkey=block.validated_by,
                num_txs=num_txs,
                num_injections=0,
                num_outliers=0,
                block_time=block.timestamp,
            )

            if (author_node := NodeStats.get(pubkey=block.validated_by)) is None:
                author_node = NodeStats(
                    pubkey=block.validated_by,
                    num_outliers=0,
                    num_injections=0,
                    num_txs=0,
                )
            author_node.num_txs += num_txs
            for tx in block.transactions:
                self.process_transaction(tx.hash, block_ts, author_node, block_delta)

            max_txs = max(ns.num_txs for ns in select(ns for ns in NodeStats))
            act_coef = activity_coef(author_node.num_txs, max_txs)
            score = trust_score(
                act_coef,
                author_node.num_injections,
                author_node.num_outliers,
                author_node.num_txs,
            )
            # update miner risk
            MinerRisk.add_datapoint_new(block.validated_by, score, block.number)

    def run(self):
        LOGGER.info("Starting Polygon rating thread...")
        while True:
            try:
                # get the block from some other thread
                block_number = TransactionEventQueue.get()

                with orm.db_session:
                    block = Block.get(number=block_number)
                    self.process_block(block)

            except Exception as e:
                traceback.print_exc()
                self.logger.error(
                    "exception when calculating the live-time transaction mean&variance happened: {}".format(
                        str(e)
                    )
                )
