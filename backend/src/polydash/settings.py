from pydantic import BaseSettings

from common.dashboard.settings import DashboardSettings


class BlockRetrieverSettings(BaseSettings):
    block_rpc_url: str = None


class W3RouterSettings(BaseSettings):
    w3_rpc_url: str = "http://localhost/rpc/update_nodes"


class PolydashSettings(DashboardSettings):
    block_retriever: BlockRetrieverSettings = BlockRetrieverSettings()
    w3_router: W3RouterSettings = W3RouterSettings()
