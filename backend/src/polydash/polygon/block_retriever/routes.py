from fastapi import APIRouter, HTTPException
from pony import orm
from polydash.common.model import Block, BlockInDB

block_router = router = APIRouter(
    prefix="/block",
    tags=["blocks"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/get_latest")
async def get_latest():
    with orm.db_session:
        blocks = Block.select().order_by(orm.desc(Block.number))[:1]
        if len(blocks) == 0:
            raise HTTPException(status_code=404, detail="No block are yet retrieved")
        result = BlockInDB.from_orm(blocks[0])
    return result
