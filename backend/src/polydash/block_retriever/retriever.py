import traceback

import requests
import json
import threading
import time
from pony import orm
from pony.orm import desc

from polydash.log import LOGGER
from polydash.block_retriever.model import Block
from polydash.block_retriever.model import Transaction
from polydash.deanon.deanonymizer import DeanonQueue
from polydash.settings import BlockRetrieverSettings
from polydash.miners_ratings.live_rating import TransactionEventQueue
from polydash.w3router_watcher.w3router_watcher import W3RouterEventQueue

alchemy_token = ""


class BlockRetriever:
    def __init__(self, settings: BlockRetrieverSettings):
        self.settings = settings
        self.__logger = LOGGER.getChild(self.__class__.__name__)

    def make_request(self, rpc_method, params):
        payload = {"jsonrpc": "2.0", "method": rpc_method, "params": params}
        headers = {"accept": "application/json", "content-type": "application/json"}
        response = requests.post(self.settings.block_rpc_url, json=payload, headers=headers)
        if response.status_code != 200:
            self.__logger.error(
                "could not make a request: {}, {}".format(
                    response.status_code, response.text
                )
            )
            return None

        json_response = json.loads(response.text)
        if json_response is None:
            self.__logger.error("could not make a request: json_response is None")
            return None
        if "error" in json_response:
            self.__logger.error(
                "could not make a request: error in the response: {}".format(
                    json_response["error"]
                )
            )
            return None
        return json_response["result"]

    def get_block(self, number=None):
        # https://docs.alchemy.com/reference/eth-getblockbynumber-polygon
        json_result = self.make_request(
            "eth_getBlockByNumber",
            ["latest" if number is None else "0x{:x}".format(number), True],
        )
        if json_result is None:
            return None

        return (
            int(json_result["number"], 16),
            int(json_result["timestamp"], 16),
            json_result["hash"],
            [(tx["hash"], tx["from"]) for tx in json_result["transactions"]],
            self.parse_txs(json_result),
            int(json_result["baseFeePerGas"], 16),
        )

    @staticmethod
    def parse_txs(json_result):
        return {
            tx["hash"]: {
                "from": tx["from"],
                "to": tx.get("to", None),
                "gas_tip_cap": int(tx.get("maxPriorityFeePerGas", "0"), 16),
                "gas_fee_cap": int(tx.get("maxFeePerGas", "0"), 16),
                "nonce": int(tx["nonce"], 16),
            }
            for tx in json_result["transactions"]
            # if tx.get("to", None) is not None
            # and int(tx.get("maxPriorityFeePerGas", "0"), 16) != 0
            # and int(tx.get("maxFeePerGas", "0"), 16) != 0
        }

    def get_block_author(self, number):
        # the result is just a string or None, so return it directly
        # https://docs.alchemy.com/reference/bor-getauthor-polygon
        return self.make_request("bor_getAuthor", ["0x{:x}".format(number)])

    def retriever_thread(self):
        self.__logger.info("block retrieved thread has started")

        next_block_number = 46699999
        with orm.db_session:
            last_block_in_db = Block.select().order_by(desc(Block.number)).first()
            if last_block_in_db is not None and last_block_in_db.number > next_block_number:
                next_block_number = last_block_in_db.number + 1
        # next_block_number = None
        # next_block_number = 0
        failure_count = 0
        while True:
            block_already_in_db = False
            if failure_count > 3:
                self.__logger.error(
                    "giving up trying to retrieve block {}, moving to the next one...".format(
                        next_block_number
                    )
                )
                failure_count = 0
                next_block_number += 1

            try:
                # first, retrieve the block
                (
                    block_number,
                    block_ts,
                    block_hash,
                    block_txs,
                    block_txs_d,
                    base_fee,
                ) = self.get_block(next_block_number)
                if block_number is None:
                    failure_count += 1
                    continue

                # second, retrieve the block's author (validator)
                author_failure_count = 0
                while (fetched_block_author := self.get_block_author(block_number)) is None:
                    if author_failure_count > 5:
                        raise "could not retrieve the author of the block"
                    self.__logger.info(
                        "trying to retrieve the author of block {} again...".format(
                            block_number
                        )
                    )
                    time.sleep(0.5)
                    author_failure_count += 1

                with orm.db_session:
                    if (block := Block.get(number=block_number)) is None:
                        block = Block(
                            number=block_number,
                            hash=block_hash,
                            validated_by=fetched_block_author,
                            timestamp=block_ts,
                        )

                        for tx in block_txs:
                            existing_transaction = Transaction.get(hash=tx[0])
                            if existing_transaction is None:
                                db_tx = Transaction(
                                    hash=tx[0],
                                    creator=tx[1],
                                    created=block_ts,
                                    block=block_number,
                                )
                            else:
                                db_tx = existing_transaction
                            if db_tx not in block.transactions:
                                block.transactions.add(db_tx)
                        orm.commit()
                        DeanonQueue.put(
                            block_number
                        )  # put the block for the deanon process to work
                        TransactionEventQueue.put(
                            block_number
                        )  # put the block for the Transaction Risks to work
                        W3RouterEventQueue.put(
                            block_number
                        )  # put the block for W3Router Watcher to work
                        self.__logger.debug(
                            "retrieved and saved into DB block with number {} and hash {}".format(
                                block_number, block_hash
                            )
                        )
                    else:
                        block_already_in_db = True

                next_block_number = block_number + 1
                failure_count = 0
            except Exception as e:
                failure_count += 1
                # TODO: instead redo the logger to save tracebacks
                traceback.print_exc()
                self.__logger.error("exception when retrieving block happened: {}".format(e))
            # Add just some timeout to avoid spamming the server
            time.sleep(0.1)
            if not block_already_in_db:
                time.sleep(1)

    def start(self):
        self.__logger.info("Starting block retriever thread...")
        threading.Thread(target=self.retriever_thread, daemon=True).start()
