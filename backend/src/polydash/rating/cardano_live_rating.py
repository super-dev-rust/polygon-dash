import queue
import threading
import traceback

from pony import orm
from pony.orm import select

from polydash.log import LOGGER
from polydash.model.cardano import CardanoTransactionRisk, CardanoBlock, CardanoBlockDelta, CardanoMinerStats, \
    CardanoMinerRisk, CardanoTransaction
from polydash.rating.injections import InjectionDetector
from polydash.rating.outliers import OutlierDetector, RiskType
from polydash.rating.rating_func import activity_coef, trust_score


class CardanoRatingProcessor:

    def __init__(self):
        self.outlier_detector = OutlierDetector(CardanoTransactionRisk)

    def process_transaction(self,
                            tx: CardanoTransaction,
                            block_author: CardanoMinerStats,
                            block_delta: CardanoBlockDelta
                            ):
        is_inject = InjectionDetector.is_transaction_injection(tx.finalized_ts, tx.first_seen_ts)
        if is_inject:
            block_author.num_injections += 1
            block_delta.num_injections += 1
            tx_risk = RiskType.RISK_INJECTION
        else:
            tx_risk = self.outlier_detector.assess_transaction_risk(tx.finalized_ts, tx.first_seen_ts)
            if tx_risk == RiskType.RISK_TOO_FAST:
                block_author.num_outliers += 1
                block_delta.num_outliers += 1
        # Record transaction risk
        CardanoTransactionRisk(
            hash=tx.hash,
            live_time=tx.finalized_ts - tx.first_seen_ts,
            risk=tx_risk.value
        )

    def process_block(self, block: CardanoBlock):
        with orm.db_session:
            if CardanoBlockDelta.get(block_number=block.number) is not None:
                # Block already processed
                return

            num_txs = len(block.transactions)
            block_delta = CardanoBlockDelta(
                block_number=block.number,
                hash=block.hash,
                pubkey=block.creator,
                num_txs=num_txs,
                num_injections=0,
                num_outliers=0,
                block_time=block.timestamp
            )

            if (author_node := CardanoMinerStats.get(pubkey=block.validated_by)) is None:
                author_node = CardanoMinerStats(
                    pubkey=block.creator,
                    num_outliers=0,
                    num_injections=0,
                    num_txs=0,
                )
            author_node.num_txs += num_txs
            for tx in block.transactions:
                self.process_transaction(tx,
                                         author_node,
                                         block_delta)

            max_txs = max(ns.num_txs for ns in select(ns for ns in CardanoMinerStats))
            act_coef = activity_coef(author_node.num_txs, max_txs)
            score = trust_score(act_coef,
                                author_node.num_injections,
                                author_node.num_outliers,
                                author_node.num_txs)

            CardanoMinerRisk.add_datapoint_new(block.validated_by,
                                               score,
                                               block.number)


CardanoBlockEventQueue = queue.Queue()


def main_loop():
    processor = CardanoRatingProcessor()

    while True:
        try:
            # get the block from some other thread
            block_number = CardanoBlockEventQueue.get()

            with orm.db_session:
                block = CardanoBlock.get(number=block_number)
                processor.process_block(block)

        except Exception as e:
            traceback.print_exc()
            LOGGER.error(
                "exception when calculating the live-time transaction mean&variance happened: {}".format(
                    str(e)
                )
            )


def start_live_time_cardano_rating():
    LOGGER.info("Starting Cardano rating thread...")
    threading.Thread(target=main_loop, daemon=True).start()
