from pydantic import BaseSettings

from polydash.common.settings import PostgresSettings
from polydash.common.settings import BlockRetrieverSettings
from polydash.polygon.w3router_watcher.settings import W3RouterSettings


class DashboardSettings(BaseSettings):
    postgres_connection: PostgresSettings = PostgresSettings()
    block_retriever: BlockRetrieverSettings = BlockRetrieverSettings()
    w3_router: W3RouterSettings = W3RouterSettings()
    port: int = 5500
    host: str = '0.0.0.0'
    log_level: str = 'ERROR'
