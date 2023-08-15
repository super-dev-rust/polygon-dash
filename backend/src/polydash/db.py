from pony import orm
from polydash.log import LOGGER
from polydash.settings import PostgresSettings

# PonyORM set up
db = orm.Database()


def start_db(settings: PostgresSettings):
    db.bind(provider='postgres', **dict(settings))
    db.generate_mapping(create_tables=True)
    LOGGER.info('database is successfully started up')
