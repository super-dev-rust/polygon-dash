from pony import orm
from polydash.log import LOGGER
from polydash.definitions import DB_FILE, DB_P2P_FILE

# PonyORM set up
db = orm.Database()
db_p2p = orm.Database()


def start_db():
    db.bind(provider='sqlite', filename=DB_FILE, create_db=True)
    db.generate_mapping(create_tables=True)
    db_p2p.bind(provider='sqlite', filename=DB_P2P_FILE, create_db=True)
    db_p2p.generate_mapping(create_tables=True)
    LOGGER.info('database is successfully started up')
