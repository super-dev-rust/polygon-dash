import queue
import threading
import math

from pony import orm

from polydash.log import LOGGER
from polydash.model.node import Node
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.plagued_node import TransactionFetched

BlockPoolHeuristic = queue.Queue()


@orm.db_session
def process_block(base_fee, block_timestamp, transactions):
    #get pending
    pending_txs = pending_transactions(block_timestamp)
    
    for tx in transactions:
        # find the transaction in the list of the ones seen by P2P
        tx_p2p = TransactionP2P.get(tx_hash=tx.hash)
        if tx_p2p is None:
            # we haven't seen it
            continue


@orm.db_session
def fill_transactions():
    #
    print("fill_transactions")
    
    
@orm.db_session
def pending_transactions(block_timestamp):
    pending_txs = []
    
    query = TransactionFetched.select(lambda t: block_timestamp < t.tx_first_seen < block_timestamp - 86400000)
    result = list(query)
    print("pending_transactions")
    return pending_txs

@orm.db_session
def new_transactions_by_price_and_nonce(base_fee, mempool):
    #
    print("new_transactions_by_price_and_nonce")



def get_effective_tip(base_fee, gas_fee_cap, gas_fee_tip):
    if gas_fee_cap < gas_fee_tip:
        return gas_fee_cap
    if gas_fee_cap - base_fee > gas_fee_tip or gas_fee_cap - base_fee == gas_fee_tip:
        return gas_fee_tip
    return gas_fee_cap - base_fee

def main_loop():
    while True:
        try:
            # get the block from some other thread
            (block_number, block_ts, block_hash, block_txs_d) = BlockPoolHeuristic.get()
            print("got block {}".format(block_number))
            with orm.db_session:
                # block base fee, extracted from the block
                # TODO: actually extract it
                base_fee = 0
                block_timestamp = 0
                process_block(base_fee, block_timestamp, block_txs_d)
        except Exception as e:
            LOGGER.error(
                "exception when calculating heuristic-a happened: {}".format(
                    str(e)
                )
            )


def start_live_time_heuristic_a():
    LOGGER.info("Starting Heuristic A thread...")
    threading.Thread(target=main_loop, daemon=True).start()
