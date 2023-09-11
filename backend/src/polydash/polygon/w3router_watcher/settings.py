from pydantic import BaseSettings


class W3RouterSettings(BaseSettings):
    w3_rpc_url: str = "http://localhost/rpc/update_nodes"
