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


class SortBy(str, Enum):
    rank = "rank"
    blocks_created = "blocks_created"
    address = "address"
    score = "score"


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


class DashboardData(BaseModel):
    data: List[MinerDisplayData]
    total: int


SORT_COLUMNS_MAP = {
    SortBy.blocks_created: MinerRisk.numblocks,
    SortBy.address: MinerRisk.pubkey,
    SortBy.score: MinerRisk.risk,
    # Essentially, sorting by rank means reverse sorting by risk
    SortBy.rank: MinerRisk.risk,
}


@router.get('/miners')
async def get_miners_info(
        page: int = 0,
        pagesize: int = 20,
        order_by: SortBy = Query(None, title="Sort By"),
        sort_order: SortOrder = Query(None, title="Sort Order")
) -> DashboardData:
    with db_session():
        # TODO: this one is horribly inefficient,
        #  probably should be optimized by caching, etc.
        miners_by_risk = MinerRisk.select().order_by(MinerRisk.risk)
        ranks = {m.pubkey: rank for rank, m in enumerate(miners_by_risk)}
        total_block_count = sum(m.numblocks for m in miners_by_risk)
        total_miners = miners_by_risk.count()

        miners = MinerRisk.select()

        if order_by:
            sort_attr = SORT_COLUMNS_MAP.get(order_by)
            if sort_order == SortOrder.desc:
                miners = miners.sort_by(desc(sort_attr))
            else:
                miners = miners.sort_by(sort_attr)

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

    return DashboardData(data=result, total=total_miners)
