
import pytest
from pony.orm import db_session

from polydash.db import db
from polydash.model.risk import MinerRisk


@pytest.fixture
def mock_db():
    db.bind(provider='sqlite', filename=':memory:', create_db=True)
    db.generate_mapping(create_tables=True)


def test_calc_risk(mock_db):
    with db_session:
        MinerRisk(miner="abc", timestamp=123, risk=345)
        r = MinerRisk.add_datapoint("abc", 124, 20)
        r = MinerRisk.add_datapoint("abc", 125, 20)

def test_get_latest_risk(mock_db):
    with db_session:
        MinerRisk.add_datapoint("abc", 123, 20)
        MinerRisk.add_datapoint("abc", 124, 20)
        MinerRisk.add_datapoint("abc", 127, 20)
        MinerRisk.add_datapoint("abc", 122, 20)
        MinerRisk.add_datapoint("ebf", 125, 30)
        MinerRisk.add_datapoint("ebf", 126, 30)
        result = list(MinerRisk.get_latest_risks())
