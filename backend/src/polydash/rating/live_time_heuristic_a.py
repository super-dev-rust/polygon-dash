import queue
import threading
import math

from pony import orm

from polydash.log import LOGGER
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.plagued_node import TransactionFetched, PlaguedBlock, PlaguedTransactionFound, PlaguedTransactionMissing

BlockPoolHeuristicQueue = queue.Queue()


GAS_PRICE = 30000000000
# zero for now
# GAS_PRICE = 0


@orm.db_session
def process_block(block_number, block_hash, base_fee, block_timestamp, transactions):
    #Let's say txes below is all txes we should see in a block except local txes
    LOGGER.debug("Processing block: {}, {}".format(block_number, block_hash))
    print("transaction length: ", len(transactions))
    pending_txs = pending_transactions_by_price_and_nonce(block_timestamp, base_fee)
    if pending_txs is None:
        LOGGER.error("Could not get pending transactions")
        return
    
    # later I should do something with this hashes
    
    transactions_found = []
    transactions_missing = []
    plagued_block = PlaguedBlock(number=block_number, hash=block_hash)
    
    for tx_hash, tx_data in transactions.items():
        if tx_hash in pending_txs:
            transactions_found.append(tx_hash)
            gas_fee_cap_pool = int(pending_txs[tx_hash].gas_fee_cap, 16)
            gas_tip_cap_pool = int(pending_txs[tx_hash].gas_tip_cap, 16)
            miner_fee_block = get_effective_tip(base_fee, tx_data["gas_fee_cap"], tx_data["gas_tip_cap"])
            miner_fee_pool = get_effective_tip(base_fee, gas_fee_cap_pool, gas_tip_cap_pool)
            plagued_block.tx_found.add(PlaguedTransactionFound(tx_hash=tx_hash, signer=tx_data["from"], nonce=tx_data["nonce"], miner_fee_block=str(miner_fee_block), miner_fee_pool=str(miner_fee_pool), block=block_number))
        else:
            transactions_missing.append(tx_hash)
            plagued_block.tx_missing.add(PlaguedTransactionMissing(tx_hash=tx_hash, signer=tx_data["from"], nonce=tx_data["nonce"], miner_fee_block=str(get_effective_tip(base_fee, tx_data["gas_fee_cap"], tx_data["gas_tip_cap"])), block=block_number))

    if (len(transactions_missing) / len(transactions)) * 100 > 30:
       plagued_block.violations = "injections"
       plagued_block.violation_severity = 1
       plagued_block.last_violation = block_timestamp

    orm.commit()

        


@orm.db_session
def pending_transactions_by_price_and_nonce(block_timestamp, base_fee):
    pending_txs = {}
    lower_bound = block_timestamp - 360000
    upper_bound = block_timestamp
    query = TransactionFetched.select_by_sql("SELECT * FROM tx_fetched WHERE tx_first_seen > $lower_bound AND tx_first_seen < $upper_bound")
    LOGGER.debug("Querying pending transactions")
    transactions = list(query)
    print("transactions length: ", len(transactions))
    if len(transactions) == 0:
        return None
    
    #until I figure how to fix go code to return transactions in order like it should be in block
    # Txes ordered when they added from fetched to pending
    # that's a slightly different task to be honest
    # listen txes and store in db is not the same
    # better will be to implement storing like in a block right in a bor.
    return {transaction.tx_hash: transaction for transaction in reversed(transactions)}
    
    for tx in transactions:
        # Convert nonce to integer
        nonce = int(tx.nonce)
        gas_fee_cap = int(tx.gas_fee_cap, 16)
        gas_tip_cap = int(tx.gas_tip_cap, 16)
        
        effective_tip = get_effective_tip(base_fee, gas_fee_cap, gas_tip_cap)
        
        #EffectiveGasTipUintLt
        if effective_tip < GAS_PRICE:
            continue 
        
        if tx.signer not in pending_txs:
            pending_txs[tx.signer] = []
        
            # Check if this transaction hash already exists in the list for this signer
        for existing_tx, _ in pending_txs[tx.signer]:
            if existing_tx.tx_hash == tx.tx_hash:
                break
        else:
            # If not, append the new transaction to the list
            pending_txs[tx.signer].append((tx, effective_tip))
            
        # if tx.signer not in pending_txs or int(pending_txs[tx.signer][0].nonce) < nonce:
        # # If signer is not in the groups yet or nonce is higher than existing transaction's nonce, add/replace the transaction
        #     pending_txs[tx.signer] = (tx, effective_tip)
    return pending_txs




def get_effective_tip(base_fee, gas_fee_cap, gas_fee_tip):
    if gas_fee_cap == 0 or gas_fee_tip == 0:
        return base_fee
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
                process_block(block_number, block_hash, base_fee, block_ts, block_txs_d)
        except Exception as e:
            LOGGER.error(
                "exception when calculating heuristic-a happened: {}".format(
                    str(e)
                )
            )


def start_live_time_heuristic_a():
    LOGGER.info("Starting Heuristic A thread...")
    threading.Thread(target=main_loop, daemon=True).start()
