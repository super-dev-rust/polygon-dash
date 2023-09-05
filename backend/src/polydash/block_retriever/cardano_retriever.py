import json
import time
import traceback

import requests
from pony import orm

from polydash.log import LOGGER
from polydash.model.cardano import CardanoBlock, CardanoTransaction
from polydash.rating.cardano_live_rating import CardanoBlockEventQueue
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

    def get_transaction_list(self, pool=None, from_datetime=None, limit=None):
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

        json_response = json.loads(response.text)
        if json_response is None:
            self.__logger.error("could not make a request: json_response is None")
            return None
        return response.json()

    def parse_json_transaction(self, json_tx):
        return (
            json_tx["tx_hash"],
            json_tx["block_time"],
            json_tx["block_hash"],
            json_tx.get('arrival_time', None),
            json_tx['pool_id'],
            json_tx["block_no"],
        )

    def retriever_thread(self):
        self.__logger.info("block retrieved thread has started")

        start_time = "2023-08-05T00:20:00.000Z"
        limit = 1000
        next_block_number = 9118742

        failure_count = 0
        block_transactions = []

        while True:
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
                tx_list = self.get_transaction_list(from_datetime=start_time, limit=limit)
                if tx_list is None:
                    failure_count += 1
                    continue

                for tx in tx_list:
                    (tx_hash,
                     block_time, block_hash,
                     arrival_time, block_creator,
                     block_number) = self.parse_json_transaction(tx)

                    if block_number != next_block_number:
                        # We start a new block, create one
                        with orm.db_session:
                            if CardanoBlock.get(block_number=block_number) is None:
                                block = CardanoBlock(
                                    block_number=block_number,
                                    block_hash=block_hash,
                                    block_creator=block_creator,
                                    timestamp=datetime_string_to_timestamp(block_time),
                                )
                                for t in block_transactions:
                                    block.transactions.add(t)
                                orm.commit()

                                CardanoBlockEventQueue.put(block_number)
                                self.__logger.debug(
                                    "retrieved and saved into DB block with number {} and hash {}".format(
                                        block_number, block_hash
                                    )
                                )

                        start_time = arrival_time
                        next_block_number += 1
                        block_transactions = []
                    else:
                        # We continue with the same block, add transactions
                        with orm.db_session:
                            if CardanoTransaction.get(hash=tx_hash) is None:
                                if arrival_time is None:
                                    # We never saw the transaction in mempool, so emulate an injection
                                    arrival_time = datetime_string_to_timestamp(block_time + 100000)
                                else:
                                    arrival_time = datetime_string_to_timestamp(arrival_time)
                                tx = CardanoTransaction(
                                    hash=tx_hash,
                                    first_seen_ts=datetime_string_to_timestamp(block_time),
                                    finalized_ts=arrival_time,
                                )
                                block_transactions.append(tx)
            except Exception as e:
                failure_count += 1
                # TODO: instead redo the logger to save tracebacks
                traceback.print_exc()
                self.__logger.error("exception when retrieving block happened: {}".format(e))
            time.sleep(20)
