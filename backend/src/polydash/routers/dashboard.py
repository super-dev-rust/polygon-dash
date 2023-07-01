from typing import List

from fastapi import APIRouter, HTTPException
from pony.orm import db_session, desc
from pydantic import BaseModel

from polydash.model.block import Block, BlockInDB
from polydash.model.risk import MinerRisk

router = APIRouter(
    prefix="/dash",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)


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
    blocks_created: int  # percentage
    violations: List[ViolationDisplayData]


@router.get('/miners')
async def get_miners_info(
        skip: int = 0,
        limit: int = 20,
        order_by: str = None,
        sort_order: str = None,
):
    with db_session:
        miners = MinerRisk.select_latest_risks()
        miners_by_risk = sorted(miners, key=lambda x: x.risk, reverse=True)
        ranks = {m.miner: rank for rank, m in enumerate(miners_by_risk)}
        total_block_count = sum(m.blocks_created for m in miners)

        result = [
            MinerDisplayData(
                score=m.risk,
                address=m.miner,
                rank=ranks[m.miner],
                name="UNKNOWN",
                blocks_created=(100 * m.blocks_created) // total_block_count,
                violations=[]
            ) for m in miners]
    return result
