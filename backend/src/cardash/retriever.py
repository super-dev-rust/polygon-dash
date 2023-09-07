import json
import time
import traceback

import requests
from pony.orm import db_session

from polydash.log import LOGGER
from polydash.p2p_data.cardano import CardanoBlock, CardanoTransaction
from polydash.miners_ratings.cardano_live_rating import CardanoBlockEventQueue
from polydash.settings import CardanoRetrieverSettings

from datetime import datetime, timezone


def datetime_string_to_timestamp(datetime_str):
    """
    Converts a datetime string in ISO 8601 format to a timestamp with milliseconds.

    Parameters:
        datetime_str (str): The datetime string in ISO 8601 format.

    Returns:
        int: The timestamp with milliseconds.
    """

    # Parse the datetime string to a datetime object
    dt_object = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Set the timezone to UTC
    dt_object = dt_object.replace(tzinfo=timezone.utc)

    # Convert the datetime object to a timestamp with milliseconds
    timestamp_ms = int(dt_object.timestamp() * 1000)

    return timestamp_ms


class CardanoRetriever:

    def __init__(self, settings: CardanoRetrieverSettings = None):
        if settings is None:
            self.settings = CardanoRetrieverSettings()
        self.__logger = LOGGER.getChild(self.__class__.__name__)
        self.base_url = self.settings.mempool_rpc_url
        self.failure_count = 0
        self.next_block_number = 9118742
        self.start_time = "2023-08-05T00:20:00.000Z"
        self.failure_count = 0
        self.limit = 1000

    def get_transactions(self, pool=None, from_datetime=None, limit=None):
        """
        Fetches a list of transactions from the given API endpoint.

        Parameters:
            pool (str, optional): Filter transactions for this pool only.
            from_datetime (datetime, optional): List transactions starting from this date/time.
            limit (int, optional): Return only this number of results. Maximum is 1000.

        Returns:
            dict: The JSON response from the API.
        """

        # Construct the API endpoint URL
        api_url = f"{self.base_url}/api/v1/tx/confirmed"

        # Initialize the parameters dictionary
        params = {}

        # Populate the parameters based on function arguments
        if pool:
            params['pool'] = pool
        if from_datetime:
            params['from'] = from_datetime
        if limit:
            params['limit'] = limit

        # Send the GET request
        response = requests.get(api_url, params=params)

        if response.status_code != 200:
            self.__logger.error(
                "could not make a request: {}, {}".format(
                    response.status_code, response.text
                )
            )
            return None

        if json.loads(response.text) is None:
            self.__logger.error("could not make a request: json_response is None")
            return None
        return response.json()

    @db_session
    def __process_single_transaction_entry(self, json_tx):
        tx_hash = json_tx["tx_hash"]
        block_time = json_tx["block_time"]
        block_hash = json_tx["block_hash"]
        arrival_time = json_tx.get('arrival_time', None)
        block_creator = json_tx['pool_id']
        block_number = json_tx["block_no"]

        if block := CardanoBlock.get(block_number=block_number) is None:
            block = CardanoBlock(
                block_number=block_number,
                block_hash=block_hash,
                block_creator=block_creator,
                timestamp=datetime_string_to_timestamp(block_time),
            )
            self.__logger.debug(
                "retrieved and saved into DB block with number {} and hash {}".format(
                    block_number, block_hash
                )
            )
            CardanoBlockEventQueue.put(self.next_block_number)

        tx = CardanoTransaction.get(tx_hash=tx_hash) or CardanoTransaction(
            hash=tx_hash,
            first_seen_ts=datetime_string_to_timestamp(block_time),
            # If we never saw the transaction in mempool, emulate an injection
            finalized_ts=datetime_string_to_timestamp(arrival_time or (block_time + 100000))
        )
        block.transactions.add(tx)
        self.__logger.debug(
            "retrieved and saved into DB transaction with hash {}, block {}".format(tx.hash, block.block_hash)
        )
        self.start_time = arrival_time
        self.next_block_number = block.block_number + 1

    def __fetch_and_process_transactions(self):
        # first, retrieve the block
        if (json_txs_list := self.get_transactions(from_datetime=self.start_time, limit=self.limit)) is None:
            self.failure_count += 1
            return

        for json_tx in json_txs_list:
            self.__process_single_transaction_entry(json_tx)

        # If we received the maximum amount of transactions
        # we requested in the batch,
        # there is a good chance we're behind the server
        # and can proceed to fetching the next batch immediately
        return len(json_txs_list) == self.limit

    def retriever_loop(self):
        self.__logger.info("block retrieved thread has started")
        retrieve_next_batch_immediately = False
        while True:
            if self.failure_count > 3:
                self.__logger.error(
                    "giving up trying to retrieve block {}, moving to the next one...".format(
                        self.next_block_number
                    )
                )
                self.failure_count = 0
                self.next_block_number += 1

            try:
                retrieve_next_batch_immediately = self.__fetch_and_process_transactions()
            except Exception as e:
                self.failure_count += 1
                # TODO: instead redo the logger to save tracebacks
                traceback.print_exc()
                self.__logger.error("exception when retrieving block happened: {}".format(e))
            if not retrieve_next_batch_immediately:
                time.sleep(20)
