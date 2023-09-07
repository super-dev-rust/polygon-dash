from fastapi import APIRouter

from polydash.deanon.model import *

deanon_router = router = APIRouter(
    prefix="/deanon",
    tags=["deanon"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


def get_list_of_deanon_nodes_by_txs_with_ips(nodes_from_db):
    """
    Helper function to find IPs of the nodes and pack them into HTTP response
    """
    result = []
    for node in nodes_from_db:
        ips = [
            PeerToIPInDB.from_orm(ip).ip for ip in PeerToIP.select(peer_id=node.peer_id)
        ]
        result.append(
            DeanonNodeByTxWithIP(node=DeanonNodeByTxInDB.from_orm(node), ips=ips)
        )
    return result


@router.get("/by_txs")
async def get_all_mappings_by_txs():
    with orm.db_session:
        result = get_list_of_deanon_nodes_by_txs_with_ips(
            DeanonNodeByTx.select().sort_by(orm.desc(DeanonNodeByTx.confidence))
        )
    return result


@router.get("/by_txs/by_pubkey/{pubkey}")
async def get_by_txs_by_pubkey(pubkey: str):
    with orm.db_session:
        result = get_list_of_deanon_nodes_by_txs_with_ips(
            DeanonNodeByTx.select(signer_key=pubkey).sort_by(
                orm.desc(DeanonNodeByTx.confidence)
            )
        )
    return result


@router.get("/by_txs/by_peer_id/{peer_id}")
async def get_by_txs_by_peer_id(peer_id: str):
    with orm.db_session:
        result = get_list_of_deanon_nodes_by_txs_with_ips(
            DeanonNodeByTx.select(peer_id=peer_id).sort_by(
                orm.desc(DeanonNodeByTx.confidence)
            )
        )
    return result


class DeanonNodeByBlockWithIP(BaseModel):
    node: DeanonNodeByBlockInDB
    ips: List[str]


def get_list_of_deanon_nodes_by_blocks_with_ips(nodes_from_db):
    """
    Helper function to find IPs of the nodes and pack them into HTTP response
    """
    result = []
    for node in nodes_from_db:
        ips = [
            PeerToIPInDB.from_orm(ip).ip for ip in PeerToIP.select(peer_id=node.peer_id)
        ]
        result.append(
            DeanonNodeByBlockWithIP(node=DeanonNodeByBlockInDB.from_orm(node), ips=ips)
        )
    return result


@router.get("/by_blocks")
async def get_all_mappings_by_blocks():
    with orm.db_session:
        result = get_list_of_deanon_nodes_by_blocks_with_ips(
            DeanonNodeByBlock.select().sort_by(orm.desc(DeanonNodeByBlock.confidence))
        )
    return result


@router.get("/by_blocks/by_pubkey/{pubkey}")
async def get_by_blocks_by_pubkey(pubkey: str):
    with orm.db_session:
        result = get_list_of_deanon_nodes_by_blocks_with_ips(
            DeanonNodeByBlock.select(signer_key=pubkey).sort_by(
                orm.desc(DeanonNodeByBlock.confidence)
            )
        )
    return result


@router.get("/by_blocks/by_peer_id/{peer_id}")
async def get_by_blocks_by_peer_id(peer_id: str):
    with orm.db_session:
        result = get_list_of_deanon_nodes_by_blocks_with_ips(
            DeanonNodeByBlock.select(peer_id=peer_id).sort_by(
                orm.desc(DeanonNodeByBlock.confidence)
            )
        )
    return result
