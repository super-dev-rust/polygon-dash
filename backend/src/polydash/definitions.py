import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

ALCHEMY_TOKEN_FILE = os.path.join(ROOT_DIR, 'alchemy_token.txt')

DB_FILE = os.path.join(ROOT_DIR, 'blocks.sqlite')
DB_P2P_FILE = os.path.join(ROOT_DIR, 'watcher.db?_journal_mode=WAL')
