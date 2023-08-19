from pydantic import BaseSettings


class PostgresSettings(BaseSettings):
    # ACHTUNG!
    # BaseSettings class gets default values from env variables.
    # So, the priority is : config > env > default.
    # As the 'user' var is typically set for the current user,
    # it will override the default from this file unless you specify it in the .yaml file.
    password: str = 'postgres'
    user: str = 'postgres'
    host: str = '/tmp/docker'
    port: int = 5432
    database: str = 'polydash'


class BlockRetrieverSettings(BaseSettings):
    block_rpc_url: str = 'https://polygon-mainnet.g.alchemy.com/v2/KcLop5WjVXKCILBnq3JBJwDYyCHHyEdt'


class PolydashSettings(BaseSettings):
    postgres_connection: PostgresSettings = PostgresSettings()
    block_retriever: BlockRetrieverSettings = BlockRetrieverSettings()
    port: int = 5500
    host: str = '0.0.0.0'
