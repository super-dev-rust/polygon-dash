from pony import orm

from polydash.dashboard.settings import PostgresSettings
from polydash.common.log import LOGGER

# PonyORM set up
db = orm.Database()


def start_db(settings: PostgresSettings, postgres_schema=None):
    options = None
    if postgres_schema:
        options = f"-c search_path={postgres_schema}"
    db.bind(provider='postgres', options=options, **dict(settings))
    db.generate_mapping(create_tables=True)
    db.create_tables(True)
    LOGGER.info('database is successfully started up')


class GetOrInsertMixin:
    @classmethod
    def get_or_insert(cls, **kwargs):
        return cls.get(**kwargs) or cls(**kwargs)
