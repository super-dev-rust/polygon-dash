import os
from polydash.log import LOGGER

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

ALCHEMY_TOKEN_FILE = os.path.join(ROOT_DIR, 'alchemy_token.txt')

DB_DIR = os.path.join(ROOT_DIR, 'dbdata')
if not os.path.exists(DB_DIR):
    LOGGER.info('creating dbdata directory')
    os.makedirs(DB_DIR)
DB_FILE = os.path.join(DB_DIR, 'blocks.sqlite')

DB_P2P_DIR = os.path.join(ROOT_DIR, 'bordb')
if not os.path.exists(DB_P2P_DIR):
    os.makedirs(DB_P2P_DIR)
DB_P2P_FILE = os.path.join(DB_P2P_DIR, 'watcher.db')
