from enum import Enum
from typing import List

from fastapi import APIRouter, HTTPException, Query
from pony.orm import db_session, desc
from pydantic import BaseModel

from polydash.model.risk import MinerRisk

router = APIRouter(
    prefix="/dash",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class ViolationDisplayData(BaseModel):
    type: str
    color: str
    last_violation: int
    violation_severity: int


class MinerDisplayData(BaseModel):
    rank: int
    score: int
    address: str
    name: str
    blocks_created: float
    violations: List[ViolationDisplayData]


@router.get('/miners')
async def get_miners_info(
        page: int = 0,
        pagesize: int = 20,
        order_by: str = None,
        sort_order: SortOrder = Query(None, title="Sort Order")
) -> MinerDisplayData:
    with db_session():
        # TODO: this one is horribly inefficient,
        #  probably should be optimized by caching, etc.
        miners_by_risk = MinerRisk.select().order_by(desc(MinerRisk.risk))
        ranks = {m.pubkey: rank for rank, m in enumerate(miners_by_risk)}
        total_block_count = sum(m.numblocks for m in miners_by_risk)

        miners = MinerRisk.select()
        if order_by:
            if (order_by_attr := getattr(MinerRisk, order_by, None)) is None:
                raise HTTPException(status_code=400, detail=f"Invalid order_by: {order_by}")
            if sort_order == SortOrder.desc:
                miners = miners.sort_by(desc(order_by_attr))
            else:
                miners = miners.sort_by(order_by_attr)

        miners = miners.page(page, pagesize)

        result = [
            MinerDisplayData(
                score=m.risk,
                address=m.pubkey,
                rank=ranks[m.pubkey],
                name="UNKNOWN",
                blocks_created=m.numblocks / total_block_count,
                violations=[]
            ) for m in miners]
    return result
