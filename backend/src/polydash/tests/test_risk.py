import pytest
from pony.orm import db_session

from polydash.db import db
from polydash.model.risk import MinerRisk


@pytest.fixture
def mock_db():
    db.bind(provider='sqlite', filename=':memory:', create_db=True)
    db.generate_mapping(create_tables=True)


def test_get_latest_risk(mock_db):
    with db_session:
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("abc", 20)
        MinerRisk.add_datapoint("ebf", 30)
        MinerRisk.add_datapoint("ebf", 30)
        print(MinerRisk.select()[:])
