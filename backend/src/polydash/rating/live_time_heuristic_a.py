import queue
import threading
import math

from pony import orm

from polydash.log import LOGGER
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.plagued_node import TransactionFetched

BlockPoolHeuristicQueue = queue.Queue()


GAS_PRICE = 30000000000
# zero for now
# GAS_PRICE = 0


@orm.db_session
def process_block(base_fee, block_timestamp, transactions):
    #Let's say txes below is all txes we should see in a block except local txes
    LOGGER.debug("Processing block")
    print("transaction length: ", len(transactions))
    pending_txs = pending_transactions_by_price_and_nonce(block_timestamp, base_fee)
    for signer_hash, tx_data in pending_txs.items():
        if tx_data[0].tx_hash in transactions:
            # we have seen it
            print("We have seen it", tx_data[0].tx_hash)
        
        # if tx_hash not in transactions:
        #     # we haven't seen it
        #     x = 1
        #     # print("We haven't seen it")
        # elif tx_data[0].nonce != transactions[tx_hash]["nonce"]:
        #     print(f"Transaction {tx_hash} has different nonces in the two sets of transactions.")
        # else:
        #     effective_tip_json = get_effective_tip(base_fee, transactions[tx_hash]["gas_fee_cap"], transactions[tx_hash]["gas_tip_cap"])
        #     if tx_data[1] != effective_tip_json:
        #         print(f"Transaction {tx_hash} has different effective tips in the two sets of transactions.")
        #     print("We have seen it")
    


    
@orm.db_session
def pending_transactions_by_price_and_nonce(block_timestamp, base_fee):
    pending_txs = {}
    lower_bound = block_timestamp - 60000
    upper_bound = block_timestamp + 10
    query = TransactionFetched.select_by_sql("SELECT * FROM tx_fetched WHERE tx_first_seen > $lower_bound and tx_first_seen < $upper_bound")
    LOGGER.debug("Querying pending transactions")
    transactions = list(query)
    for tx in transactions:
        # Convert nonce to integer
        nonce = int(tx.nonce)
        gas_fee_cap = int(tx.gas_fee_cap, 16)
        gas_tip_cap = int(tx.gas_tip_cap, 16)
        
        effective_tip = get_effective_tip(base_fee, gas_fee_cap, gas_tip_cap)
        
        #EffectiveGasTipUintLt
        if effective_tip < GAS_PRICE:
            continue 
        
        if tx.signer not in pending_txs or int(pending_txs[tx.signer][0].nonce) < nonce:
        # If signer is not in the groups yet or nonce is higher than existing transaction's nonce, add/replace the transaction
            pending_txs[tx.signer] = (tx, effective_tip)
    pending_transactions = list(pending_txs.values())
    print("pending_transactions", len(pending_transactions))
    # print("pending_transactions", pending_txs)
    return pending_txs


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
            (block_number, block_ts, block_hash, block_txs_d, base_fee) = BlockPoolHeuristicQueue.get()
            with orm.db_session:
                process_block(base_fee, block_ts, block_txs_d)
        except Exception as e:
            LOGGER.error(
                "exception when calculating heuristic-a happened: {}".format(
                    str(e)
                )
            )


def start_live_time_heuristic_a():
    LOGGER.info("Starting Heuristic A thread...")
    threading.Thread(target=main_loop, daemon=True).start()
