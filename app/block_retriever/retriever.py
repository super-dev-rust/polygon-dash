import requests
import json
import threading
import time
from pony import orm
from app.model.block import Block
from app.log import LOGGER
from app.definitions import ALCHEMY_TOKEN_FILE

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
    return int(json_result['number'], 16), json_result['hash']


def get_block_author(number):
    # the result is just a string or None, so return it directly
    # https://docs.alchemy.com/reference/bor-getauthor-polygon
    return make_request('bor_getAuthor', ['0x{:x}'.format(number)])


def retriever_thread():
    LOGGER.info('block retrieved thread has started')
    next_block_number = None
    while True:
        try:
            # first, retrieve the block
            (fetched_block_number, fetched_block_hash) = get_block(next_block_number)
            if fetched_block_number is None:
                continue

            # second, retrieve the block's author (validator)
            fetched_block_author = get_block_author(fetched_block_number)
            while fetched_block_author is None:
                time.sleep(0.5)
                fetched_block_author = get_block_author(fetched_block_number)

            # finally, save it in DB
            with orm.db_session:
                block = Block(number=fetched_block_number, hash=fetched_block_hash, validated_by=fetched_block_author)
                orm.commit()
            LOGGER.debug('retrieved and saved into DB block with number {} and hash {}'.format(fetched_block_number,
                                                                                               fetched_block_hash))

            next_block_number = fetched_block_number + 1
        except Exception as e:
            LOGGER.error('exception when retrieving block happened: {}'.format(e))
        time.sleep(2)


def start_retriever():
    LOGGER.info('Starting block retriever thread...')
    threading.Thread(target=retriever_thread, daemon=True).start()
