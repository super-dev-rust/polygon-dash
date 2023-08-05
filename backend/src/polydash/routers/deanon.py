from fastapi import APIRouter, HTTPException
from pony import orm

from polydash.model.deanon_node_by_tx import DeanonNodeByTx, DeanonNodeByTxInDB
from polydash.model.deanon_node_by_block import DeanonNodeByBlock, DeanonNodeByBlockInDB

router = APIRouter(
    prefix="/deanon",
    tags=["deanon"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/by_txs")
async def get_all_mappings_by_txs():
    with orm.db_session:
        nodes = DeanonNodeByTx.select().sort_by(orm.desc(DeanonNodeByTx.confidence))
        result = [DeanonNodeByTxInDB.from_orm(n) for n in nodes]
    return result


@router.get("/by_txs/by_pubkey/{pubkey}")
async def get_by_txs_by_pubkey(pubkey: str):
    with orm.db_session:
        nodes = DeanonNodeByTx.select(signer_key=pubkey).sort_by(
            orm.desc(DeanonNodeByTx.confidence)
        )
        result = [DeanonNodeByTxInDB.from_orm(n) for n in nodes]
    return result


@router.get("/by_txs/by_peer_id/{peer_id}")
async def get_by_txs_by_peer_id(peer_id: str):
    with orm.db_session:
        nodes = DeanonNodeByTx.select(peer_id=peer_id).sort_by(
            orm.desc(DeanonNodeByTx.confidence)
        )
        result = [DeanonNodeByTxInDB.from_orm(n) for n in nodes]
    return result


@router.get("/by_blocks")
async def get_all_mappings_by_blocks():
    with orm.db_session:
        nodes = DeanonNodeByBlock.select().sort_by(
            orm.desc(DeanonNodeByBlock.confidence)
        )
        result = [DeanonNodeByBlockInDB.from_orm(n) for n in nodes]
    return result


@router.get("/by_blocks/by_pubkey/{pubkey}")
async def get_by_blocks_by_pubkey(pubkey: str):
    with orm.db_session:
        nodes = DeanonNodeByBlock.select(signer_key=pubkey).sort_by(
            orm.desc(DeanonNodeByBlock.confidence)
        )
        result = [DeanonNodeByBlockInDB.from_orm(n) for n in nodes]
    return result


@router.get("/by_blocks/by_peer_id/{peer_id}")
async def get_by_blocks_by_peer_id(peer_id: str):
    with orm.db_session:
        nodes = DeanonNodeByBlock.select(peer_id=peer_id).sort_by(
            orm.desc(DeanonNodeByBlock.confidence)
        )
        result = [DeanonNodeByBlockInDB.from_orm(n) for n in nodes]
    return result
