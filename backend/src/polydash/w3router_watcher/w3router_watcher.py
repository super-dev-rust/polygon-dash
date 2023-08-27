import queue
import threading
import traceback
import requests

from pony import orm

from polydash.log import LOGGER
from polydash.model.risk import MinerRisk
from polydash.model.deanon_node_by_tx import DeanonNodeByTx
from polydash.model.deanon_node_by_block import DeanonNodeByBlock
from polydash.model.peer_to_ip import PeerToIP

W3RouterEventQueue = queue.Queue()

TOP_NODES_LIST_SIZE = 10


class W3RouterWatcher:
    """
    Purpose of this class is to recalculate the list of the most trusted nodes every time a new block
    is received and, if there are any changes, push them into the W3Router itself
    """

    last_top_nodes_list = []

    def send_nodes_to_router(self):
        LOGGER.info(
            "Sending new list of nodes to the W3Router: {}".format(
                self.last_top_nodes_list
            )
        )
        response = requests.post(
            "http://localhost/rpc/update_nodes", json=self.last_top_nodes_list
        )
        if response.status_code != 200:
            LOGGER.error(
                "W3Router has returned {} as status code".format(response.status_code)
            )

    def check_top_nodes(self):
        global TOP_NODES_LIST_SIZE

        new_top_nodes = {}
        top_nodes_select_offset = 0
        current_priority = 1

        while True:
            if len(new_top_nodes) >= TOP_NODES_LIST_SIZE:
                break

            # get the list from the DB
            new_top_nodes_from_db = MinerRisk.select_by_sql(
                "SELECT * FROM minerrisk ORDER BY risk DESC LIMIT {} OFFSET {}".format(
                    TOP_NODES_LIST_SIZE, top_nodes_select_offset
                )
            )
            top_nodes_select_offset += TOP_NODES_LIST_SIZE
            if len(new_top_nodes_from_db) == 0:
                # we have exhausted the list of the nodes
                break

            # build a new list, including the IP addresses
            for node in new_top_nodes_from_db:
                # try to get peer ID of the node using two tables
                deanoned_node = (
                    DeanonNodeByBlock.select(signer_key=node.pubkey)
                    .order_by(orm.desc(DeanonNodeByBlock.confidence))
                    .limit(1)
                )
                if len(deanoned_node) == 0:
                    deanoned_node = (
                        DeanonNodeByTx.select(signer_key=node.pubkey)
                        .order_by(orm.desc(DeanonNodeByTx.confidence))
                        .limit(1)
                    )
                if len(deanoned_node) == 0:
                    # we don't know peer ID of this node, moving on
                    continue

                # now, try to get IP address of that node
                node_ip = (
                    PeerToIP.select(peer_id=deanoned_node[0].peer_id)
                    .order_by(orm.desc(PeerToIP.id))
                    .limit(1)
                )
                if len(node_ip) == 0:
                    # we don't know IP of this node, moving on
                    continue

                # we have found IP of that node, memorize it if it wasn't in the list before
                ip = node_ip[0].ip
                if ip in new_top_nodes.values():
                    continue
                new_top_nodes[current_priority] = ip
                current_priority += 1

                # if we have gathered enough nodes information, finish
                if len(new_top_nodes) >= TOP_NODES_LIST_SIZE:
                    break

        if new_top_nodes != self.last_top_nodes_list:
            self.last_top_nodes_list = new_top_nodes
            self.send_nodes_to_router()


def main_loop():
    watcher = W3RouterWatcher()
    while True:
        try:
            # get the block from some other thread; we're not really going to use the block number (at least for now),
            # but we want to receive the notification itself
            _ = W3RouterEventQueue.get()
            with orm.db_session:
                watcher.check_top_nodes()
        except Exception as e:
            traceback.print_exc()
            LOGGER.error(
                "exception when checking for the top nodes in W3Router Watcher happened: {}".format(
                    str(e)
                )
            )


def start_w3router_watcher():
    LOGGER.info("Starting W3Router Watcher thread...")
    threading.Thread(target=main_loop, daemon=True).start()
