import queue
import threading
import traceback

from pony.orm import db_session

from polydash.common.log import LOGGER
from polydash.common.model import Block
from polydash.polygon.deanon.model import DeanonNodeByBlock, PeerToIP, DeanonNodeByTx
from polydash.polygon.p2p_data.model import TransactionP2P, BlockP2P

DeanonQueue = queue.Queue()


class Deanonymizer(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = LOGGER.getChild(self.__class__.__name__)

    @db_session
    def calculate_confidence_by_block(self, block):
        """
        Increase the confidence of the relation between the peer, from which
        we first saw this block, and the creator of this block
        """
        if (block_from_p2p := BlockP2P.get_first_by_hash(block.hash)) is None:
            # we haven't seen this block over P2P, nothing can be done
            return

        # if no such node is remembered by us yet, create it
        deanon_node = DeanonNodeByBlock.get_or_insert(
            signer_key=block.validated_by, peer_id=block_from_p2p.peer
        )
        # just increase the confidence of this mapping
        deanon_node.confidence += 1

        # also put the information about IP of this peer into the DB if we don't remember it already
        PeerToIP.get_or_insert(
            peer_id=block_from_p2p.peer, ip=block_from_p2p.peer_remote_addr
        )

    @db_session
    def calculate_confidence_by_tx(self, block):
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
                signer_key=block.validated_by, peer_id=tx_p2p.peer_id
            ).confidence += 1

    def run(self):
        self.logger.info("Starting Deanonymizer thread...")
        while True:
            try:
                # get the block from some other thread
                block_number = DeanonQueue.get()
                with db_session:
                    block = Block.get(number=block_number)
                    self.calculate_confidence_by_block(block)
                    self.calculate_confidence_by_tx(block)
            except Exception as e:
                traceback.print_exc()
                self.logger.error(
                    "exception when calculating the deanonymizer confidence happened: {}".format(
                        str(e)
                    )
                )
