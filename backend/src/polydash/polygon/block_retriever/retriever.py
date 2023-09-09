import traceback

import requests
import json
import threading
import time
from pony import orm
from pony.orm import desc, db_session

from polydash.common.log import LOGGER
from polydash.common.model import Block
from polydash.common.model import Transaction
from polydash.common.settings import BlockRetrieverSettings
from polydash.polygon.deanon.deanonymizer import DeanonQueue
from polydash.miners_ratings.live_rating import TransactionEventQueue


class BlockRetriever:
    def __init__(self, settings: BlockRetrieverSettings):
        self.settings = settings
        self.__logger = LOGGER.getChild(self.__class__.__name__)
        self.failure_count = 0
        self.block_already_in_db = False

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
        return json_result

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

    def get_block_author(self, block_number):
        # the result is just a string or None, so return it directly
        # https://docs.alchemy.com/reference/bor-getauthor-polygon

        failure_count = 0
        while (author := self.make_request("bor_getAuthor", ["0x{:x}".format(block_number)])) is None:
            if failure_count > 5:
                raise "could not retrieve the author of the block"
            self.__logger.info(
                "trying to retrieve the author of block {} again...".format(
                    block_number
                )
            )
            time.sleep(0.5)
            failure_count += 1
        return author

    @db_session
    def __process_single_block(self, block_json, block_author):
        # first, retrieve the block
        block_number = int(block_json["number"], 16)
        block_ts = int(block_json["timestamp"], 16)
        block_hash = block_json["hash"]
        block_txs = [(tx["hash"], tx["from"]) for tx in block_json["transactions"]]
        # block_txs_d = self.parse_txs(block_json),
        # base_fee = int(block_json["baseFeePerGas"], 16),

        if Block.exists(number=block_number):
            self.block_already_in_db = True
        else:
            block = Block(
                number=block_number,
                hash=block_hash,
                validated_by=block_author,
                timestamp=block_ts,
            )

            for tx in block_txs:
                db_tx = Transaction.get(hash=tx[0]) or Transaction(
                    hash=tx[0],
                    creator=tx[1],
                    created=block_ts,
                    block=block_number,
                )
                if db_tx not in block.transactions:
                    block.transactions.add(db_tx)
            orm.commit()

            # put the block for the deanon process to work
            DeanonQueue.put(block_number)

            # put the block for the Transaction Risks to work
            TransactionEventQueue.put(block_number)

            self.__logger.debug(
                "retrieved and saved into DB block with number {} and hash {}".format(
                    block_number, block_hash
                )
            )

    @staticmethod
    def get_next_block_number():
        next_block_number = 46699999
        with orm.db_session:
            last_block_in_db = Block.select().order_by(desc(Block.number)).first()
            if last_block_in_db is not None and last_block_in_db.number > next_block_number:
                next_block_number = last_block_in_db.number + 1
        return next_block_number

    def handle_failure(self, block_number):
        self.__logger.error(
            f"giving up trying to retrieve block {block_number}, moving to the next one..."
        )
        self.failure_count = 0
        return block_number + 1

    def process_block(self, block_number):
        try:
            self.failure_count += 1
            block_json = self.get_block(block_number)
            block_number = int(block_json.get("number"), 16)
            if block_json is None or block_number is None:
                return block_number
            block_author = self.get_block_author(block_number)
            self.__process_single_block(block_json, block_author)
            self.failure_count = 0
            return block_number + 1
        except Exception as e:
            traceback.print_exc()
            self.__logger.error("exception when retrieving block happened: {}".format(e))
            return block_number

    def retriever_loop(self):
        self.__logger.info("block retrieved thread has started")
        next_block_number = self.get_next_block_number()
        while True:
            self.block_already_in_db = False
            if self.failure_count > 3:
                next_block_number = self.handle_failure(next_block_number)
            next_block_number = self.process_block(next_block_number)
            # Add just some timeout to avoid spamming the server
            time.sleep(0.1 if self.block_already_in_db else 1)

    def start(self):
        self.__logger.info("Starting block retriever thread...")
        threading.Thread(target=self.retriever_loop, daemon=True).start()
