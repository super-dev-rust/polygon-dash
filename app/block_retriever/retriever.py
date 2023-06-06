import requests
import json
from pony import orm
from app.model.block import Block

alchemy_token = ''


def get_latest_block():
    # global alchemy_token
    # if len(alchemy_token) == 0:
    #     with open('alchemy_token.txt', 'r') as file:
    #         alchemy_token = file.read()

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
        print('could not make a request: {}, {}'.format(response.status_code, response.text))
        return False

    json_response = json.loads(response.text)
    with orm.db_session:
        block = Block(number=int(json_response['result']['number'], 16), hash=json_response['result']['hash'])
        orm.commit()

    # TODO: get the author of the block, also put transactions inside, also should be in separate worker thread
