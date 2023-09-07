from fastapi import APIRouter, HTTPException
from pony import orm
from polydash.miners_ratings.model import TransactionRisk, TransactionRiskOut

transaction_risk_router = router = APIRouter(
    prefix="/tx_risk",
    tags=["transactions"],
    # dependencies=[Depends(get_token_header)],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Bad value in request"},
    },
)


@router.get("")
async def get_all_txs():
    with orm.db_session:
        txs = TransactionRisk.select()
        result = [TransactionRiskOut.from_orm(tx) for tx in txs]
    return result


@router.get("/latest/{n}")
async def get_latest_n(n: int):
    if n <= 0:
        raise HTTPException(
            status_code=422, detail="Number of transactions must be greater than 0"
        )
    with orm.db_session:
        txs = TransactionRisk.select_by_sql(
            "SELECT * from TransactionRisk ORDER BY id DESC LIMIT {}".format(n)
        )
        result = [TransactionRiskOut.from_orm(tx) for tx in txs]
    return result


@router.get("/latest/risked/{n}")
async def get_latest_risked_txs_n(n: int):
    """
    Risks: 0 means transaction was too fast, 1 means transaction was too slow
    """
    if n <= 0:
        raise HTTPException(
            status_code=422, detail="Number of transactions must be greater than 0"
        )
    with orm.db_session:
        txs = TransactionRisk.select_by_sql(
            "SELECT * from TransactionRisk WHERE risk IS NOT NULL ORDER BY id DESC LIMIT {}".format(
                n
            )
        )
        result = [TransactionRiskOut.from_orm(tx) for tx in txs]
    return result


@router.get("/{tx_hash}")
async def get_tx(tx_hash: str):
    with orm.db_session:
        node = TransactionRisk[tx_hash]
        result = TransactionRiskOut.from_orm(node)
    return result
