from polydash.common.db import db
from polydash.common.log import LOGGER
from polydash.common.settings import PostgresSettings
from polydash.common.upgrade import check_db_version


def start_db(settings: PostgresSettings, network_name=None):
    db.bind(provider="postgres", **dict(settings))
    db.generate_mapping(create_tables=True)
    check_db_version(network_name)
    LOGGER.info("database is successfully started up")
