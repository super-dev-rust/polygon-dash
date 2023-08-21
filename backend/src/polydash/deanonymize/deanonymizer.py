import queue
import threading
import traceback

from pony import orm

from polydash.log import LOGGER
from polydash.model.block_p2p import BlockP2P
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.deanon_node_by_tx import DeanonNodeByTx
from polydash.model.deanon_node_by_block import DeanonNodeByBlock
from polydash.model.peer_to_ip import PeerToIP
from polydash.model.block import Block

DeanonymizerQueue = queue.Queue()


@orm.db_session
def calculate_confidence_by_block(block):
    """
    Increase the confidence of the relation between the peer, from which
    we first saw this block, and the creator of this block
    """
    if (block_from_p2p := BlockP2P.get_first_by_hash(block.hash)) is None:
        # we haven't seen this block over P2P, nothing can be done
        return

    # if no such node is remembered by us yet, create it
    deanon_node = DeanonNodeByBlock.get_or_insert(
        signer_key=block.validated_by, peer_id=block_from_p2p.peer)
    # just increase the confidence of this mapping
    deanon_node.confidence += 1

    # also put the information about IP of this peer into the DB if we don't remember it already
    PeerToIP.get_or_insert(peer_id=block_from_p2p.peer, ip=block_from_p2p.peer_remote_addr)


@orm.db_session
def calculate_confidence_by_tx(block):
    """
    Increase the confidence of the relation between the peer, from which
    we first saw transactions from this block, and the creator of this block
    """
    for tx in block.transactions:
        if (tx_p2p := TransactionP2P.get_first_by_hash(tx.hash)) is None:
            # we haven't seen it
            continue

        # if there is no such node is remembered by us yet, create it
        # and just increase the confidence of this mapping
        DeanonNodeByTx.get_or_insert(
            signer_key=block.validated_by, peer_id=tx_p2p.peer_id).confidence += 1


def main_loop():
    while True:
        try:
            # get the block from some other thread
            block_number = DeanonymizerQueue.get()
            with orm.db_session:
                block = Block.get(number=block_number)
                calculate_confidence_by_block(block)
                calculate_confidence_by_tx(block)
        except Exception as e:
            traceback.print_exc()
            LOGGER.error(
                "exception when calculating the deanonymizer confidence happened: {}".format(
                    str(e)
                )
            )


def start_deanonymizer():
    LOGGER.info("Starting Deanonymizer thread...")
    threading.Thread(target=main_loop, daemon=True).start()
