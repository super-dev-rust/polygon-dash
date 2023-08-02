import queue
import threading

from pony import orm

from polydash.log import LOGGER
from polydash.model.block_p2p import BlockP2P
from polydash.model.transaction_p2p import TransactionP2P
from polydash.model.deanon_node_by_tx import DeanonNodeByTx
from polydash.model.deanon_node_by_block import DeanonNodeByBlock
from polydash.model.peer_to_ip import PeerToIP

DeanonymizerQueue = queue.Queue()


@orm.db_session
def calculate_confidence_by_block(block):
    """
    Increase the confidence of the relation between the peer, from which
    we first saw this block, and the creator of this block
    """
    block_from_p2p = BlockP2P.get_by_sql(
        'SELECT * FROM block_fetched WHERE block_hash="{}" ORDER BY first_seen_ts LIMIT 1'.format(
            block.hash
        )
    )
    if block_from_p2p is None:
        # we haven't seen this block over P2P, nothing can be done
        return

    deanon_node = DeanonNodeByBlock.get(
        signer_key=block.validated_by, peer_id=block_from_p2p.peer
    )
    if deanon_node is None:
        # no such node is remembered by us yet, create it
        deanon_node = DeanonNodeByBlock(
            signer_key=block.validated_by, peer_id=block_from_p2p.peer, confidence=1
        )
    else:
        # just increase the confidence of this mapping
        deanon_node.confidence += 1

    # also put the information about IP of this peer into the DB if we don't remember it already
    peer_ip = PeerToIP.get(
        peer_id=block_from_p2p.peer, ip=block_from_p2p.peer_remote_addr
    )
    if peer_ip is None:
        peer_ip = PeerToIP(
            peer_id=block_from_p2p.peer, ip=block_from_p2p.peer_remote_addr
        )


@orm.db_session
def calculate_confidence_by_tx(block):
    """
    Increase the confidence of the relation between the peer, from which
    we first saw transactions from this block, and the creator of this block
    """
    for tx in block.transactions:
        tx_p2p = TransactionP2P.get_by_sql(
            'SELECT * FROM tx_summary WHERE tx_hash="{}" ORDER BY tx_first_seen LIMIT 1'.format(
                tx.hash
            )
        )
        if tx_p2p is None:
            # we haven't seen it
            return

        deanon_node = DeanonNodeByTx.get(
            signer_key=block.validated_by, peer_id=tx_p2p.peer_id
        )
        if deanon_node is None:
            # no such node is remembered by us yet, create it
            deanon_node = DeanonNodeByTx(
                signer_key=block.validated_by, peer_id=tx_p2p.peer_id, confidence=1
            )
        else:
            # just increase the confidence of this mapping
            deanon_node.confidence += 1


def main_loop():
    while True:
        try:
            # get the block from some other thread
            block = DeanonymizerQueue.get()

            calculate_confidence_by_block(block)
            calculate_confidence_by_tx(block)
        except Exception as e:
            LOGGER.error(
                "exception when calculating the deanonymizer confidence happened: {}".format(
                    str(e)
                )
            )


def start_deanonymizer():
    LOGGER.info("Starting Deanonymizer thread...")
    threading.Thread(target=main_loop, daemon=True).start()
