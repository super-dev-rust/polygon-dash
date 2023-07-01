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
    #blocks_created: int
    #violations: List[ViolationDisplayData]


@router.get('/miners')
async def get_miners_info(
        skip: int = 0,
        limit: int = 20,
        order_by: str = None,
        sort_order: str = None,
):
    with db_session:
        miners = MinerRisk.get_latest_risks()[skip:limit]
        if not miners:
            raise HTTPException(status_code=404, detail="No data found for this query ")
        for m in miners:

        result = [MinerDisplayData]
    return result
