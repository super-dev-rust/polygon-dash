from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pony.orm import db_session, desc
from pydantic import BaseModel

from polydash.common.log import LOGGER
from polydash.common.model import Block

TRUST_SCORE_Y_AXIS = "percentage"
VIOLATIONS_Y_AXIS = "num_violations"
BIN_SIZE = 1

CHARTJS_OPTIONS = {
    "scales": {
        TRUST_SCORE_Y_AXIS: {
            "max": 100,
            "min": 0,
            "type": 'linear',
            "position": 'left'
        },
        VIOLATIONS_Y_AXIS: {
            "ticks": {"beginAtZero": True, "color": "red"},
            "type": 'logarithmic',
            "grid": {"display": False},
            "position": 'right'
        },
        "x": {
            "beginAtZero": True,
            "stacked": True
        }
    },
    "responsive": True,
    "legend": {
        "labels": {
            "fontColor": 'red',
        }
    }
}
from polydash.miners_ratings.model import BlockDelta, MinerRisk, MinerRiskHistory

dashboard_router = router = APIRouter(
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
    score: float
    address: str
    name: str
    blocks_created: float
    violations: List[ViolationDisplayData]


class MinerBlocksData(BaseModel):
    block_number: int
    block_hash: str
    risk: float


OUTLIERS_COLOR = "#FFA450"
TRUST_COLOR = "#32a852"


class MinerChartDataset(BaseModel):
    fill: bool = False
    order: int
    type: Optional[str]
    label: str
    borderColor: str
    stack: str
    backgroundColor: str
    data: List[float | None]
    tension: Optional[str]
    yAxisID: str = TRUST_SCORE_Y_AXIS


class MinerChartData(BaseModel):
    labels: List[str]
    datasets: List[MinerChartDataset]
    options: Optional[dict] = CHARTJS_OPTIONS
    total: int


class DashboardData(BaseModel):
    data: List[MinerDisplayData]
    total: int


class PieChartDataset(BaseModel):
    label: str
    data: List[int]
    backgroundColor: List[str]
    hoverBackgroundColor: List[str]


class MinersTrustDistribution(BaseModel):
    labels: List[str]
    pie_chart: PieChartDataset


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
        order_by: SortBy = Query(SortBy.rank, title="Sort By"),
        sort_order: SortOrder = Query(None, title="Sort Order"),
) -> DashboardData:
    with db_session():
        # TODO: this one is horribly inefficient,
        #  probably should be optimized by caching, etc.
        miners_by_risk = MinerRisk.select().order_by(desc(MinerRisk.risk))
        ranks = {m.pubkey: rank for rank, m in enumerate(miners_by_risk)}
        violations_by_miner = {m.pubkey: [] for m in miners_by_risk}

        for block in BlockDelta.select().order_by(desc(BlockDelta.block_number)).limit(3000):
            # only show last three violations for a node
            if len(violations_by_miner[block.pubkey]) > 2:
                continue
            if block.num_injections:
                violations_by_miner[block.pubkey].append(
                    ViolationDisplayData(
                        type="injection",
                        color="#D22B2B",
                        last_violation=block.block_time,
                        violation_severity=block.num_injections,
                    )
                )
            if block.num_outliers:
                violations_by_miner[block.pubkey].append(
                    ViolationDisplayData(
                        type="outlier",
                        color=OUTLIERS_COLOR,
                        last_violation=block.block_time,
                        violation_severity=block.num_outliers,
                    )
                )

        total_block_count = sum(m.numblocks for m in miners_by_risk)
        total_miners = miners_by_risk.count()

        miners = MinerRisk.select()

        if order_by:
            sort_attr = SORT_COLUMNS_MAP.get(order_by)
            if order_by == SortBy.rank:
                if sort_order == SortOrder.desc:
                    miners = miners.sort_by(sort_attr)
                else:
                    miners = miners.sort_by(desc(sort_attr))
            else:
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
async def get_miner_info(address: str, last_blocks: int = 100) -> MinerChartData:
    with db_session():
        if MinerRisk.get(pubkey=address) is None:
            raise HTTPException(status_code=404, detail="Miner not found")

        blocks_history = MinerRiskHistory.select().where(pubkey=address).order_by(MinerRiskHistory.block_number).limit(
            last_blocks)
        if not blocks_history:
            return MinerChartData(labels=[], datasets=[], blocks_data=[])

        LOGGER.debug("Blocks history: %s", blocks_history)
        labels = []
        risk_data = []
        violations_data = []
        outliers_data = []
        blocks_data = []
        skipped_blocks_data = []

        data_bin = []
        violations_sum = 0
        outliers_sum = 0
        transactions_sum = 0
        num_blocks_added = 0
        for block in blocks_history:
            if (plagued_block := BlockDelta.get(block_number=block.number)) is None:
                continue

            if (blocks_data and
                    (blocks_delta := (block.block_number - blocks_data[-1].block_number)) > 1):
                # This miner skipped some blocks, so insert and additional datapoint
                # in the chart to indicate it
                skipped_blocks_data.append(blocks_delta)
                labels.append(f"skipped blocks")
                risk_data.append(None)
                violations_data.append(None)
                outliers_data.append(None)

            # Populate blocks data for now, maybe it will be used later
            blocks_data.append(
                MinerBlocksData(
                    block_number=block.number,
                    block_hash=plagued_block.hash,
                    risk=block.risk,
                )
            )

            num_blocks_added += 1
            violations_sum += plagued_block.num_injections
            outliers_sum += plagued_block.num_outliers
            transactions_sum += Block.get(number=block.block_number).transactions.count()
            if num_blocks_added == BIN_SIZE:
                # Populate labels(block numbers as strings) for chart
                labels.append(str(block.number))
                skipped_blocks_data.append(None)
                risk_data.append(100.0 * block.risk)
                violations_data.append(((100.0 * violations_sum)/transactions_sum) if transactions_sum else None)
                outliers_data.append(((100.0 * outliers_sum)/transactions_sum) if transactions_sum else None)
                print (violations_sum, transactions_sum)
                num_blocks_added = 0
                violations_sum = 0
                outliers_sum = 0
                transactions_sum = 0

        datasets = [
            MinerChartDataset(
                order=1,
                type="line",
                label="Trust Score (%)",
                borderColor=TRUST_COLOR,
                backgroundColor=TRUST_COLOR,
                stack="risk_score",
                data=risk_data,
                yAxisID=TRUST_SCORE_Y_AXIS,
                tension="0.5"
            ), MinerChartDataset(
                order=2,
                label="Injections",
                borderColor="#CD212A",
                stack="violations",
                backgroundColor="#CD212A",
                data=violations_data,
                yAxisID=TRUST_SCORE_Y_AXIS,
            ), MinerChartDataset(
                order=3,
                label="Outliers (suspected injections)",
                borderColor=OUTLIERS_COLOR,
                stack="violations",
                backgroundColor=OUTLIERS_COLOR,
                data=outliers_data,
                yAxisID=TRUST_SCORE_Y_AXIS,
            ), MinerChartDataset(
                order=4,
                label="Skipped blocks",
                borderColor="#000000",
                stack="skipped_blocks",
                backgroundColor="#000000",
                data=skipped_blocks_data,
                yAxisID=VIOLATIONS_Y_AXIS,
            ), ]

        return MinerChartData(
            labels=labels,
            datasets=datasets,
            total=len(labels))


@router.get("/trust-distribution")
async def get_miner_trust_distribution() -> MinersTrustDistribution:
    with db_session():
        miners = MinerRisk.select()
        labels = ["Trusted", "Suspicious", "Untrusted"]

        trusted = 0  # 100-85
        suspicious = 0  # 84-64
        untrusted = 0  # 63-0

        for miner in miners:
            if miner.risk * 100 >= 85:
                trusted += 1
            elif 64 <= miner.risk * 100 < 85:
                untrusted += 1
            else:
                suspicious += 1

        result = MinersTrustDistribution(
            labels=labels,
            pie_chart=PieChartDataset(
                label="PieChart",
                data=[trusted, suspicious, untrusted],
                backgroundColor=["#58d68d", "#f7dc6f", "#ec7063"],
                hoverBackgroundColor=["#2ecc71", "#f4d03f", "#e74c3c"]
            )
        )

    return result
