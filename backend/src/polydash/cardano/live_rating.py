import queue
import threading
import traceback

from pony import orm
from pony.orm import select

from polydash.common.log import LOGGER
from polydash.miners_ratings.injections import InjectionDetector
from polydash.miners_ratings.model import (
    TransactionRisk,
    BlockDelta,
    NodeStats,
    MinerRisk,
)
from polydash.miners_ratings.outliers import OutlierDetector, RiskType
from polydash.miners_ratings.rating_func import activity_coef, trust_score
from polydash.common.model import Transaction, Block

CardanoBlockEventQueue = queue.Queue()


class CardanoRatingProcessor(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(CardanoRatingProcessor, self).__init__(*args, **kwargs)
        self.outlier_detector = OutlierDetector(TransactionRisk)
        self.logger = LOGGER.getChild(self.__class__.__name__)

    def process_transaction(
        self, tx: Transaction, block_author: NodeStats, block_delta: BlockDelta
    ):
        # If we never saw the transaction in mempool, emulate an injection
        is_inject = InjectionDetector.is_transaction_injection(
            tx.finalized_ts, tx.first_seen_ts
        )
        if is_inject:
            tx_risk = RiskType.RISK_INJECTION
            block_author.num_injections += 1
            block_delta.num_injections += 1
        else:
            tx_risk = self.outlier_detector.assess_transaction_risk(
                tx.finalized_ts, tx.first_seen_ts
            )
            if tx_risk == RiskType.RISK_TOO_FAST:
                block_author.num_outliers += 1
                block_delta.num_outliers += 1
        # Record transaction risk
        TransactionRisk(
            hash=tx.hash,
            live_time=(tx.finalized_ts - tx.first_seen_ts) if tx.first_seen_ts else 0,
            risk=tx_risk.value,
        )

    def process_block(self, block: Block):
        with orm.db_session:
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
                self.process_transaction(tx, author_node, block_delta)

            max_txs = max(ns.num_txs for ns in select(ns for ns in NodeStats))
            act_coef = activity_coef(author_node.num_txs, max_txs)
            score = trust_score(
                act_coef,
                author_node.num_injections,
                author_node.num_outliers,
                author_node.num_txs,
            )

            MinerRisk.add_datapoint_new(block.validated_by, score, block.number)

    def run(self):
        self.logger.info("Starting Cardano rating thread...")
        while True:
            try:
                # get the block from some other thread
                block_number = CardanoBlockEventQueue.get()

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
