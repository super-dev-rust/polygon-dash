import math
import queue
import threading
import traceback

from pony import orm
from pony.orm import select
from tdigest import TDigest

from polydash.log import LOGGER
from polydash.model.block import Block
from polydash.model.block_p2p import BlockP2P
from polydash.model.node_risk import NodeStats, BlockDelta
from polydash.model.risk import MinerRisk
from polydash.model.transaction import Transaction
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.transaction_risk import (
    TransactionRisk,
    RiskType,
)

TransactionEventQueue = queue.Queue()

# get updated with every call to calculate_mean_variance
INITIALIZED_GLOBALS = False
GLOBAL_MEAN = 0
GLOBAL_VARIANCE = 0
GLOBAL_COUNTED_TXS = 0


def try_initialize_globals(digest: TDigest):
    with orm.db_session:
        # Select last 10000 transactions and update digest
        txs = TransactionRisk.select().order_by(TransactionRisk.id)[:10000]
        for t in txs:
            digest.update(t.live_time)


def record_injection(author_node: NodeStats, block_delta: BlockDelta):
    author_node.num_injections += 1
    block_delta.num_injections += 1


def record_outlier(author_node: NodeStats, block_delta: BlockDelta):
    author_node.num_outliers += 1
    block_delta.num_outliers += 1


def process_transaction(tx_hash: str,
                        tx_finalized: int,
                        block_delta: BlockDelta, author_node: NodeStats,
                        digest: TDigest) -> RiskType:
    # find the transaction in the list of the ones seen by P2P
    if (tx_p2p := TransactionP2P.get_first_by_hash(tx_hash)) is None:
        # We haven't seen this transaction. Record an injection for the node
        record_injection(author_node, block_delta)
        return RiskType.RISK_INJECTION

    # get the live-time of this transaction
    live_time = tx_finalized - tx_p2p.tx_first_seen

    # The transaction was seen too late. Record an injection for the node
    if live_time < -10000:
        record_injection(author_node, block_delta)
        return RiskType.RISK_INJECTION
    # Record as outlier
    if live_time < 0:
        record_outlier(author_node, block_delta)
        return RiskType.RISK_TOO_FAST

    digest.update(live_time)
    if live_time <= digest.percentile(1):
        risk = RiskType.RISK_TOO_FAST
        record_outlier(author_node, block_delta)
    elif live_time >= digest.percentile(99):
        risk = RiskType.RISK_TOO_SLOW
    else:
        risk = RiskType.NO_RISK

    # Record transaction Risk
    tx_risk = TransactionRisk(
        hash=tx_hash,
        risk=risk.value,
        live_time=live_time,
    )
    return risk


def process_block(block: Block, digest: TDigest):
    if (block_from_p2p := BlockP2P.get_first_by_hash(block.hash)) is not None:
        block_ts = block_from_p2p.first_seen_ts
    else:
        block_ts = block.timestamp * 1000

    block_delta = BlockDelta(
        block_number=block.number,
        hash=block.hash,
        pubkey=block.validated_by,
        num_txs=len(block.transactions),
        num_injections=0,
        num_outliers=0,
        block_time=block.timestamp
    )

    if (author_node := NodeStats.get(pubkey=block.validated_by)) is None:
        author_node = NodeStats(
            pubkey=block.validated_by,
            num_outliers=0,
            num_injections=0,
            num_txs=0,
        )
    num_txs = 0
    num_injects = 0
    num_outliers = 0
    for tx in block.transactions:
        risk = process_transaction(tx.hash, block_ts,
                                   block_delta, author_node, digest)
        num_txs += 1
        if risk == RiskType.RISK_INJECTION:
            num_injects += 1
        elif risk == RiskType.RISK_TOO_FAST:
            num_outliers += 1
    author_node.num_txs += num_txs

    # Get max number of transactions from NodeStats
    max_txs = max(ns.num_txs for ns in select(ns for ns in NodeStats))
    c = author_node.num_txs / max_txs
    d = 1 / (1 + math.exp(-12 * (c - 0.4)))
    d = 1 if c == 1 else d
    MinerRisk.add_datapoint_new(block.validated_by,
                                d, num_injects, num_outliers,
                                num_txs, block.number)


def main_loop():
    digest = TDigest()

    try_initialize_globals(digest)

    while True:
        try:
            # get the block from some other thread
            block_number = TransactionEventQueue.get()

            with orm.db_session:
                block = Block.get(number=block_number)
                process_block(block, digest)

        except Exception as e:
            traceback.print_exc()
            LOGGER.error(
                "exception when calculating the live-time transaction mean&variance happened: {}".format(
                    str(e)
                )
            )


def start_live_time_rating_calc():
    LOGGER.info("Starting LiveTimeTransaction thread...")
    threading.Thread(target=main_loop, daemon=True).start()
