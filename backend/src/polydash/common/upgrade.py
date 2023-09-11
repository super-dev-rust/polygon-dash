from pony.orm import db_session

from polydash.common.log import LOGGER
from polydash.common.model import AuxiliaryData

DB_VERSION_KEY = "dbVersion"
CURRENT_DB_VERSION = "20"
NETWORK_NAME_KEY = "network"


@db_session
def upgrade_from_v1(db):
    # Create a cursor object
    conn = db.get_connection()
    cur = db.get_connection().cursor()

    cur.execute("BEGIN;")
    cur.execute("""
        ALTER TABLE block
        ALTER COLUMN timestamp
        TYPE bigint USING timestamp::bigint;
    """)

    cur.execute("""
        ALTER TABLE blockdelta
        ALTER COLUMN block_time
        TYPE bigint USING block_time::bigint;
    """)

    cur.execute("""
        ALTER TABLE transaction
        DROP COLUMN created;
    """)

    cur.execute("""
        CREATE TABLE auxillarydata(
        key TEXT PRIMARY KEY,
        value TEXT
        ); 
    """)

    cur.execute("""
        INSERT INTO auxillarydata(key, value) 
        VALUES ('dbVersion', '20'), ('network', 'polygon'); 
    """)

    conn.commit()

    # Close cursor and connection
    cur.close()


def upgrade_db(version):
    # TBD
    exit(1)
    pass


@db_session
def check_db_version(network_name):
    version = v.value if (v := AuxiliaryData.get(key=DB_VERSION_KEY)) else None
    if version is None:
        # New DB, add current version
        AuxiliaryData(key=DB_VERSION_KEY, value=CURRENT_DB_VERSION)
        AuxiliaryData(key=NETWORK_NAME_KEY, value=network_name)
    else:
        if (name_in_db := AuxiliaryData.get(key=NETWORK_NAME_KEY).value) != network_name:
            LOGGER.error(
                "DB network name mismatch. Expected: %s, Actual: %s. Starting migration",
                network_name,
                name_in_db,
            )
            exit(1)
        if version != CURRENT_DB_VERSION:
            LOGGER.warn(
                "DB version mismatch. Expected: %s, Actual: %s. Starting DB ugrade",
                CURRENT_DB_VERSION,
                version,
            )
            upgrade_db(version)
