import random
import string

import pytest
from pony.orm import db_session

from polydash.db import db
from polydash.common.model import Block
from polydash.miners_ratings.model import NodeStats, BlockDelta
from polydash.miners_ratings.model import MinerRisk
from polydash.common.model import Transaction
from polydash.polygon.p2p_data.model import TransactionP2P
from polydash.miners_ratings.live_rating import PolygonRatingProcessor


@pytest.fixture
def mock_db():
    db.bind(provider="sqlite", filename=":memory:", create_db=True)
    db.generate_mapping(create_tables=True)


def test_process_block(mock_db):
    with db_session:
        block_ts = 100
        miner_id = "miner1"
        block_hash = "abc"

        block = Block(
            number=1, hash=block_hash, validated_by=miner_id, timestamp=block_ts
        )
        block_ts *= 1000
        for i in range(100):
            # generate random string of 10 chars
            tx_hash = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
            creator = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )

            block.transactions.add(
                Transaction(
                    hash=tx_hash,
                    creator=creator,
                    created=block_ts,
                    block=1,
                )
            )
            # 0 - 1: injections
            # Regular tx
            peer_id = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=5)
            )
            if 2 <= i <= 95:
                delta = random.randint(4500, 5000)
                TransactionP2P(
                    tx_hash=tx_hash, peer_id=peer_id, tx_first_seen=block_ts - delta
                )
            elif 96 <= i <= 97:
                # fast transactions
                delta = random.randint(0, 200)
                TransactionP2P(
                    tx_hash=tx_hash, peer_id=peer_id, tx_first_seen=block_ts - delta
                )
            elif i == 98:
                # Transaction with small negative delta
                delta = random.randint(10, 9999)
                TransactionP2P(
                    tx_hash=tx_hash, peer_id=peer_id, tx_first_seen=block_ts + delta
                )
            elif i == 99:
                # Transaction with big negative delta
                delta = random.randint(10001, 20000)
                TransactionP2P(
                    tx_hash=tx_hash, peer_id=peer_id, tx_first_seen=block_ts + delta
                )
        assert block.transactions.count() == 100
        PolygonRatingProcessor().process_block(block)

        block_delta = BlockDelta.get(block_number=1)
        node_stats = NodeStats.get(pubkey=miner_id)
        risk_data = MinerRisk.get(pubkey=miner_id)

        assert block_delta.num_txs == 100

        assert node_stats.num_txs == 100
        assert node_stats.num_injections == 3
        assert node_stats.num_outliers <= 6

        assert risk_data.numblocks == 1
        assert round(risk_data.risk, 2) == 0.76


def test_get_new_risk(mock_db):
    with db_session:
        MinerRisk.add_datapoint_new("abc", 0.9, 1)
        MinerRisk.add_datapoint_new("abc", 0.9, 2)
        MinerRisk.add_datapoint_new("abc", 0.9, 3)
        MinerRisk.add_datapoint_new("abc", 0.9, 4)
        MinerRisk.add_datapoint_new("ebf", 1.0, 5)
        MinerRisk.add_datapoint_new("ebf", 1.0, 6)

        assert len(MinerRisk.select()[:]) == 2
        assert MinerRisk.select()[:][0].pubkey == "abc"
        assert round(MinerRisk.select()[:][0].risk, 2) == 0.9
        assert MinerRisk.select()[:][0].numblocks == 4

        assert MinerRisk.select()[:][1].pubkey == "ebf"
        assert round(MinerRisk.select()[:][1].risk, 2) == 1.0
        assert MinerRisk.select()[:][1].numblocks == 2
