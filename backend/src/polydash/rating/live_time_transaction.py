import queue
import threading
import math
import traceback

from pony import orm

from polydash.log import LOGGER
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.node_risk import NodeRisk
from polydash.model.block import Block
from polydash.model.transaction_risk import (
    TransactionRisk,
    RISK_TOO_FAST,
    RISK_TOO_SLOW,
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
            (old_variance + old_mean**2) * old_number_of_values + new_value**2
        ) / new_number_of_values - new_mean**2
    else:
        new_variance = 0

    # return the results
    return new_mean, new_variance, new_number_of_values, too_low, too_big


def process_transaction(tx, node_pubkey):
    # find the transaction in the list of the ones seen by P2P
    with orm.db_session:
        # Pony kept throwing exception at me with both generator and lambda select syntax, so raw SQL
        if (tx_p2p := TransactionP2P.get_first_by_hash(tx.hash)) is None:
            return

    # get the live-time of this transaction
    live_time = tx.created - tx_p2p.tx_first_seen
    if live_time <= 0:
        return

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
        risk = RISK_TOO_SLOW
    elif too_big:
        risk = RISK_TOO_FAST

    # save the values into DB
    with orm.db_session:
        # of our new transaction risk
        TransactionRisk(
            hash=tx.hash,
            risk=risk,
            live_time=live_time,
            global_mean=mean,
            global_variance=variance,
            global_counted_txs=counted_txs,
        )

        # and also of the node, which is responsible for that transaction
        if too_low or too_big:
            author_node = NodeRisk.get_or_insert(pubkey=node_pubkey)
            if too_low:
                author_node.too_fast_txs += 1
            else:
                author_node.too_slow_txs += 1


def main_loop():
    try_initialize_globals()

    while True:
        try:
            # get the block from some other thread
            block_number = TransactionEventQueue.get()
            with orm.db_session:
                block = Block.get(number=block_number)

                # update our internal mean-variance state and find outliers
                for tx in block.transactions:
                    process_transaction(tx, block.validated_by)
        except Exception as e:
            traceback.print_exc()
            LOGGER.error(
                "exception when calculating the live-time transaction mean&variance happened: {}".format(
                    str(e)
                )
            )


def start_live_time_transaction_heuristic():
    LOGGER.info("Starting LiveTimeTransaction thread...")
    threading.Thread(target=main_loop, daemon=True).start()
