import requests
import json
import threading
import time
from pony import orm
from polydash.model.block import Block
from polydash.model.transaction import Transaction
from polydash.log import LOGGER
from polydash.definitions import ALCHEMY_TOKEN_FILE
from polydash.rating.live_time_heuristic import EventQueue

alchemy_token = ''


def get_alchemy_url():
    global alchemy_token
    if len(alchemy_token) == 0:
        with open(ALCHEMY_TOKEN_FILE, 'r') as file:
            alchemy_token = file.read()

    return "https://polygon-mainnet.g.alchemy.com/v2/{}".format(alchemy_token)


def make_request(rpc_method, params):
    payload = {
        "jsonrpc": "2.0",
        "method": rpc_method,
        "params": params
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(get_alchemy_url(), json=payload, headers=headers)
    if response.status_code != 200:
        LOGGER.error('could not make a request: {}, {}'.format(response.status_code, response.text))
        return None

    json_response = json.loads(response.text)
    if json_response is None or json_response['result'] == 'null':
        return None
    return json_response['result']


def get_block(number=None):
    # https://docs.alchemy.com/reference/eth-getblockbynumber-polygon
    json_result = make_request('eth_getBlockByNumber', ["latest" if number is None else '0x{:x}'.format(number), True])
    if json_result is None:
        return None

    return int(json_result['number'], 16), int(json_result['timestamp'], 16), json_result['hash'], [
        (tx['hash'], tx['from']) for tx in
        json_result['transactions']]


def get_block_author(number):
    # the result is just a string or None, so return it directly
    # https://docs.alchemy.com/reference/bor-getauthor-polygon
    return make_request('bor_getAuthor', ['0x{:x}'.format(number)])


def retriever_thread():
    LOGGER.info('block retrieved thread has started')
    # set to None to begin from the latest block; set to some block ID to begin with it
    # next_block_number = 44239277
    next_block_number = None
    while True:
        try:
            # first, retrieve the block
            (block_number, block_ts, block_hash, block_txs) = get_block(next_block_number)
            if block_number is None:
                continue

            # second, retrieve the block's author (validator)
            fetched_block_author = get_block_author(block_number)
            while fetched_block_author is None:
                time.sleep(0.5)
                fetched_block_author = get_block_author(block_number)

            # finally, save it in DB
            with orm.db_session:
                block = Block(number=block_number, hash=block_hash, validated_by=fetched_block_author)
                for tx in block_txs:
                    block.transactions.add(Transaction(hash=tx[0], creator=tx[1], created=block_ts, block=block_number))
                orm.commit()
                EventQueue.put(block)  # put the block for the heuristics to be updated
            LOGGER.debug('retrieved and saved into DB block with number {} and hash {}'.format(block_number,
                                                                                               block_hash))

            next_block_number = block_number + 1
        except Exception as e:
            LOGGER.error('exception when retrieving block happened: {}'.format(e))
        time.sleep(2)


def start_retriever():
    LOGGER.info('Starting block retriever thread...')
    threading.Thread(target=retriever_thread, daemon=True).start()
