from fastapi import APIRouter
from pony import orm
from polydash.model.node import Node, NodeInDB

router = APIRouter(
    prefix="/node",
    tags=["nodes"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get('')
async def get_all_nodes():
    with orm.db_session:
        nodes = Node.select()
        result = [NodeInDB.from_orm(n) for n in nodes]
    return result


@router.get('/{pubkey}')
async def get_node(pubkey: str):
    with orm.db_session:
        node = Node[pubkey]
        result = NodeInDB.from_orm(node)
    return result
