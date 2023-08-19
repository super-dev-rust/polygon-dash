import pytest
from pony.orm import db_session

from polydash.db import db
from polydash.model.risk import MinerRisk


@pytest.fixture
def mock_db():
    db.bind(provider='sqlite', filename=':memory:', create_db=True)
    db.generate_mapping(create_tables=True)


def test_get_new_risk(mock_db):
    with db_session:
        MinerRisk.add_datapoint_new("abc", 0.9, 1, 1, 10, 1)
        MinerRisk.add_datapoint_new("abc", 0.9, 1, 1, 10, 2)
        MinerRisk.add_datapoint_new("abc", 0.9, 1, 1, 10, 3)
        MinerRisk.add_datapoint_new("abc", 0.9, 1, 1, 10, 4)
        MinerRisk.add_datapoint_new("ebf", 1.0, 1, 1, 2, 5)
        MinerRisk.add_datapoint_new("ebf", 1.0, 1, 1, 2, 6)

        assert len(MinerRisk.select()[:]) == 2
        assert MinerRisk.select()[:][0].pubkey == "abc"
        assert round(MinerRisk.select()[:][0].risk, 2) == 0.81
        assert MinerRisk.select()[:][0].numblocks == 4

        assert MinerRisk.select()[:][1].pubkey == "ebf"
        assert round(MinerRisk.select()[:][1].risk, 2) == 0.5
        assert MinerRisk.select()[:][1].numblocks == 2


def test_get_latest_risk(mock_db):
    with db_session:
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("ebf", 30)
        MinerRisk.add_datapoint("ebf", 30)
        print(MinerRisk.select()[:])
