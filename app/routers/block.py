from fastapi import APIRouter, HTTPException
from pony import orm
from app.block_retriever.retriever import get_latest_block
from app.model.block import Block, BlockInDB

router = APIRouter(
    prefix="/block",
    tags=["blocks"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get('/trigger_get_latest')
async def trigger_get_latest():
    get_latest_block()
    return {"message": "Triggered the latest block's retrieval"}


@router.get('/get_latest')
async def get_latest():
    with orm.db_session:
        blocks = Block.select().order_by(orm.desc(Block.number))[:1]
        if len(blocks) == 0:
            raise HTTPException(status_code=404, detail="No block are yet retrieved")
        result = BlockInDB.from_orm(blocks[0])
    return result
