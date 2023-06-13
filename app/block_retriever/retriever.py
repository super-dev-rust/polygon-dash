import requests
import json
import threading
import time
from pony import orm
from app.model.block import Block
from app.log import LOGGER
from app.definitions import ALCHEMY_TOKEN_FILE

alchemy_token = ''


def get_latest_block():
    global alchemy_token
    if len(alchemy_token) == 0:
        with open(ALCHEMY_TOKEN_FILE, 'r') as file:
            alchemy_token = file.read()

    url = "https://polygon-mainnet.g.alchemy.com/v2/{}".format(alchemy_token)
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": ["latest", True]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        LOGGER.error('could not make a request: {}, {}'.format(response.status_code, response.text))
        return False

    json_response = json.loads(response.text)
    block_number = int(json_response['result']['number'], 16)
    block_hash = json_response['result']['hash']
    with orm.db_session:
        block = Block(number=block_number, hash=block_hash)
        orm.commit()
    LOGGER.debug('retrieved and saved into DB block with number {} and hash {}'.format(block_number, block_hash))


def retriever_thread():
    LOGGER.info('block retrieved thread has started')
    while True:
        try:
            get_latest_block()
        except Exception as e:
            LOGGER.error('exception when retrieving block happened: {}'.format(e))
        time.sleep(2)


def start_retriever():
    LOGGER.info('Starting block retriever thread...')
    threading.Thread(target=retriever_thread, daemon=True).start()
