from enum import Enum
from typing import List

from fastapi import APIRouter, HTTPException, Query
from pony.orm import db_session, desc
from pydantic import BaseModel

from polydash.log import LOGGER
from polydash.model.risk import MinerRisk, MinerRiskHistory
from polydash.model.plagued_node import PlaguedBlock

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


class BlockViolationsData(BaseModel):
    type: str
    color: str # #D22B2B for injection, #D2B22B for censoring, #2BD22B for reordering
    amount: int # 1 for now


class MinerDetailedBlocksData(BaseModel):
    block_number: int
    block_hash: str
    risk: int
    violations: List[BlockViolationsData]


class MinerDetailedData(BaseModel):
    data: List[MinerDetailedBlocksData]
    total: int


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


@router.get("/miners")
async def get_miners_info(
    page: int = 0,
    pagesize: int = 20,
    order_by: SortBy = Query(None, title="Sort By"),
    sort_order: SortOrder = Query(None, title="Sort Order"),
) -> DashboardData:
    with db_session():
        # TODO: this one is horribly inefficient,
        #  probably should be optimized by caching, etc.
        miners_by_risk = MinerRisk.select().order_by(MinerRisk.risk)
        ranks = {m.pubkey: rank for rank, m in enumerate(miners_by_risk)}
        last_blocks = {m.pubkey: m.block_number for m in miners_by_risk}
        violations_by_miner = {m.pubkey: [] for m in miners_by_risk}
        for pubkey, block_number in last_blocks.items():
            plagued_block = PlaguedBlock.get(number=block_number)
            if (
                plagued_block == None
                or plagued_block.violations == ""
                or plagued_block.last_violation == None
            ):
                continue
            violations_by_miner[pubkey].append(
                ViolationDisplayData(
                    type=plagued_block.violations,
                    color="#D22B2B",
                    last_violation=plagued_block.last_violation,
                    violation_severity=1,
                )
            )

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
                violations=violations_by_miner[
                    m.pubkey
                ],
            )
            for m in miners
        ]

    return DashboardData(data=result, total=total_miners)


@router.get("/miners/{address}")
async def get_miner_info(address: str, last_blocks: int = 50) -> MinerDetailedData:
    with db_session():
        
        miner = MinerRisk.get(pubkey=address)
        if not miner:
            raise HTTPException(status_code=404, detail="Miner not found")

        blocks_history = MinerRiskHistory.select_by_sql("SELECT * FROM MinerRiskHistory WHERE pubkey = $address ORDER BY block_number DESC LIMIT $last_blocks")        
        if not blocks_history:
            return MinerDetailedData(data=[], total=0)
        
        detailed_blocks = []

        for block in list(blocks_history):
            plagued_block = PlaguedBlock.get(number=block.block_number)
            if plagued_block is not None:
                #TODO:there should be a function that parse violations string
                # and return a list of violations prepared for MinerDetailedBlocksData
                # for now only one violation is supported
                violations = [
                    BlockViolationsData(
                        type=plagued_block.violations,
                        color="#D22B2B",
                        amount=1
                    )
                ]
                detailed_blocks.append(
                    MinerDetailedBlocksData(
                        block_number=block.block_number,
                        block_hash=plagued_block.hash,
                        risk=block.risk,
                        violations=violations
                    )
                )
       
        return MinerDetailedData(data=detailed_blocks, total=len(detailed_blocks))
