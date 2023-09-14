import json
import logging
import threading
import time
import traceback
import requests
from pony import orm
from pony.orm import db_session

from datetime import datetime, timezone

from polydash.cardano.live_rating import CardanoBlockEventQueue
from polydash.common.log import LOGGER
from polydash.common.model import Transaction, Block
from polydash.common.settings import BlockRetrieverSettings

DATETIME_WITH_MS = "%Y-%m-%dT%H:%M:%S.%fZ"


def datetime_string_to_timestamp(datetime_str):
    dt_object = datetime.strptime(datetime_str, DATETIME_WITH_MS)
    dt_object = dt_object.replace(tzinfo=timezone.utc)
    return int(dt_object.timestamp() * 1000)


def timestamp_to_datetime_string(timestamp):
    dt_object = datetime.utcfromtimestamp(timestamp / 1000)
    return dt_object.strftime(DATETIME_WITH_MS)


class CardanoBlockRetriever(threading.Thread):
    def __init__(self, *args, settings: BlockRetrieverSettings = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings or BlockRetrieverSettings()
        self.logger = LOGGER.getChild(self.__class__.__name__)
        self.base_url = self.settings.block_rpc_url
        self.start_time = datetime_string_to_timestamp("2023-08-05T00:20:00.000Z")
        self.failure_count = 0
        self.limit = 1000
        with db_session:
            last_added_block = Block.select().order_by(Block.number.desc()).first()
            self.current_block_number = (
                last_added_block.number if last_added_block else 0
            )

    def get_transactions(self, pool=None, from_datetime=None, limit=None):
        """
        Fetches a list of transactions from the given API endpoint.
        """
        api_url = f"{self.base_url}/api/v1/tx/confirmed"
        
        params = {
            "pool": pool,
            "from": timestamp_to_datetime_string(from_datetime),
            "limit": limit,
        }
        response = requests.get(api_url, params=params)

        if response.status_code != 200:
            self.logger.error(
                "Could not make a request: {}, {}, {}".format(
                    response.status_code, response.text, params
                )
            )
            return None

        if json.loads(response.text) is None:
            self.logger.error("could not make a request: json_response is None")
            return None
        return response.json()

    @db_session
    def __process_single_transaction_entry(self, json_tx, block):
        tx_hash = json_tx["tx_hash"]
        arrival_time = (
            datetime_string_to_timestamp(json_tx["arrival_time"])
            if json_tx.get("arrival_time")
            else None
        )

        tx = Transaction.get(hash=tx_hash) or Transaction(
            hash=tx_hash,
            first_seen_ts=arrival_time,
            finalized_ts=block.timestamp,
            block=block,
        )
        block.transactions.add(tx)
        self.logger.debug(
            "retrieved and saved into DB transaction with hash {}, block {}".format(
                tx.hash, block.hash
            )
        )
        self.start_time = block.timestamp

    @db_session
    def __get_or_create_block(self, json_tx):
        block_time = datetime_string_to_timestamp(json_tx["block_time"])
        block_hash = json_tx["block_hash"]
        block_creator = json_tx["pool_id"]
        block_number = json_tx["block_no"]
        if (block := Block.get(number=block_number)) is None:
            block = Block(
                number=block_number,
                hash=block_hash,
                validated_by=block_creator,
                timestamp=block_time,
            )
            self.logger.debug(
                "retrieved and saved into DB block with number {} and hash {}".format(
                    block_number, block_hash
                )
            )
        return block

    def __fetch_and_process_transactions(self):
        # first, retrieve the block
        if (
            json_txs_list := self.get_transactions(
                from_datetime=self.start_time, limit=self.limit
            )
        ) is None:
            self.failure_count += 1
            return

        with db_session:
            for json_tx in json_txs_list:
                if self.current_block_number != (
                    tx_block_number := json_tx["block_no"]
                ):
                    # We must commit transaction by block granularity
                    # to properly feed the analyzer thread
                    orm.commit()
                    CardanoBlockEventQueue.put(self.current_block_number)
                    self.current_block_number = tx_block_number
                block = self.__get_or_create_block(json_tx)
                self.__process_single_transaction_entry(json_tx, block)
                # ACHTUNG!
                # Watch out for block boundary aliasing with request limit
                # and app restarts! Potentially, we can lose some processing triggers
                # in case of aliasing.

        # If we received the maximum amount of transactions
        # we requested in the batch,
        # there is a good chance we're behind the server
        # and can proceed to fetching the next batch immediately
        return len(json_txs_list) == self.limit

    def retriever_loop(self):
        self.logger.info("block retrieved thread has started")
        retrieve_next_batch_immediately = False
        while True:
            try:
                retrieve_next_batch_immediately = (
                    self.__fetch_and_process_transactions()
                )
            except Exception as e:
                self.failure_count += 1
                # TODO: instead redo the logger to save tracebacks
                traceback.print_exc()
                self.logger.error(
                    "exception when retrieving block happened: {}".format(e)
                )
            if not retrieve_next_batch_immediately:
                # time.sleep(20)
                time.sleep(1)

    def start(self):
        self.logger.info("Starting block retriever thread...")
        threading.Thread(target=self.retriever_loop, daemon=True).start()
