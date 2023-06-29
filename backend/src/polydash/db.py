from pony import orm
from polydash.log import LOGGER

# PonyORM set up
db = orm.Database()


def start_db():
    db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
    db.generate_mapping(create_tables=True)
    LOGGER.info('database is successfully started up')
