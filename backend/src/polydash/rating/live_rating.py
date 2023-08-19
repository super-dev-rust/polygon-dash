import queue
import threading
import math
import traceback

from pony import orm

from polydash.log import LOGGER
from polydash.model.node_risk import NodeStats, BlockDelta
from polydash.model.risk import MinerRisk
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.node_risk import NodeRisk
from polydash.model.block import Block
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


def try_initialize_globals():
    global INITIALIZED_GLOBALS
    global GLOBAL_MEAN
    global GLOBAL_VARIANCE
    global GLOBAL_COUNTED_TXS

    if INITIALIZED_GLOBALS:
        return

    # initialize the values of GLOBAL_MEAN & GLOBAL_VARIANCE with the last values from DB (if they exist)
    with orm.db_session:
        last_tx_risk = TransactionRisk.select().order_by(TransactionRisk.id).first()
    if last_tx_risk is not None:
        GLOBAL_MEAN = last_tx_risk.global_mean
        GLOBAL_VARIANCE = last_tx_risk.global_variance
        GLOBAL_COUNTED_TXS = last_tx_risk.global_counted_txs


def calculate_mean_variance(new_value, old_mean, old_variance, old_number_of_values):
    """
    Pure function to calculate mean&variance of the new value taking into
    account the old values and the size of the data set
    """

    # first, see if this value is an outlier in relation to the old values
    too_low = False
    too_big = False
    if old_variance != 0:
        deviation = (new_value - old_mean) / math.sqrt(old_variance)
        too_low = deviation < -3
        too_big = deviation > 3

    # second, update the values of mean and variance
    new_number_of_values = old_number_of_values + 1
    new_mean = (old_mean * old_number_of_values + new_value) / new_number_of_values
    if new_number_of_values > 1:
        new_variance = (
                               (old_variance + old_mean ** 2) * old_number_of_values + new_value ** 2
                       ) / new_number_of_values - new_mean ** 2
    else:
        new_variance = 0

    # return the results
    return new_mean, new_variance, new_number_of_values, too_low, too_big


def record_injection(author_node: NodeStats, block_delta: BlockDelta):
    with orm.db_session:
        author_node.num_injections += 1
        author_node.num_txs += 1

        block_delta.num_txs += 1
        block_delta.num_injections += 1


def record_outlier(author_node: NodeStats, block_delta: BlockDelta):
    # TODO: FIX
    with orm.db_session:
        author_node.num_outliers += 1
        author_node.num_txs += 1

        block_delta.num_txs += 1
        block_delta.num_outliers += 1


def process_transaction(tx, node_pubkey, block_delta: BlockDelta, author_node: NodeStats, ) -> RiskType:
    # find the transaction in the list of the ones seen by P2P
    with orm.db_session:
        if (tx_p2p := TransactionP2P.get_first_by_hash(tx.hash)) is None:
            # We haven't seen this transaction. Record an injection for the node
            record_injection(author_node, block_delta)
            return RiskType.RISK_INJECTION

    # get the live-time of this transaction
    live_time = tx.created - tx_p2p.tx_first_seen

    # The transaction was seen too late. Record an injection for the node
    if live_time < -10000:
        record_injection(author_node, block_delta)
        return RiskType.RISK_INJECTION
    # Record as outlier
    if live_time < 0:
        record_outlier(author_node, block_delta)
        return RiskType.RISK_TOO_FAST

    # calculate the values
    global GLOBAL_MEAN
    global GLOBAL_VARIANCE
    global GLOBAL_COUNTED_TXS
    mean, variance, counted_txs, too_low, too_big = calculate_mean_variance(
        live_time, GLOBAL_MEAN, GLOBAL_VARIANCE, GLOBAL_COUNTED_TXS
    )

    # update the values
    GLOBAL_MEAN = mean
    GLOBAL_VARIANCE = variance
    GLOBAL_COUNTED_TXS = counted_txs
    risk = None
    if too_low:
        risk = RiskType.RISK_TOO_SLOW
    elif too_big:
        risk = RiskType.RISK_TOO_FAST
    else:
        risk = RiskType.NO_RISK

    # save the values into DB
    with orm.db_session:
        # of our new transaction risk
        tx_risk = TransactionRisk(
            hash=tx.hash,
            risk=risk.value,
            live_time=live_time,
            global_mean=mean,
            global_variance=variance,
            global_counted_txs=counted_txs,
        )

        if too_low:
            record_outlier(author_node, block_delta)
        return risk



def main_loop():
    try_initialize_globals()

    while True:
        try:
            # get the block from some other thread
            block_number = TransactionEventQueue.get()

            with orm.db_session:
                block = Block.get(number=block_number)

                block_delta = BlockDelta(
                    block_number=block.number,
                    hash=block.hash,
                    pubkey=block.validated_by,
                    num_txs=0,
                    num_injections=0,
                    num_violations=0,
                    block_time=block.timestamp
                )

                author_node = NodeStats.get(pubkey=block.validated_by)
                if author_node is None:
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
                risk = process_transaction(tx, block.validated_by, block_delta, author_node)
            num_txs += 1
            if risk.RISK_INJECTION:
                num_injects += 1
            elif risk.RISK_TOO_FAST:
                num_injects += 1

            with orm.db_session:
                # Get max number of transactions from NodeStats
                max_txs = max(ns.num_txs for ns in NodeStats)
                c = author_node.num_txs / max_txs
                d = 1 / (1 + math.exp(-12 * (c - 0.4)))
                MinerRisk.add_datapoint_new(block.validated_by,
                                            d, num_injects, num_outliers,
                                            num_txs, block.number)
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
