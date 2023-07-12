import pytest
import time
import random
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pony.orm import db_session

from polydash.db import db
from polydash.model.risk import MinerRisk
from polydash.model.plagued_node import PlaguedBlock
from polydash.routers.dashboard import router


VIOLATIONS = ("injections", "censoring", "reordering", "")


# class PlaguedBlock(db.Entity):
#     number = orm.PrimaryKey(int)
#     hash = orm.Required(str)
#     violations = orm.Optional(str)  # injections, censoring, reordering
#     tx_missing = orm.Set(PlaguedTransactionMissing)
#     tx_found = orm.Set(PlaguedTransactionFound)
#     last_violation = orm.Optional(int)
#     violation_severity = orm.Optional(int)


def add_mock_datapoint_with_mock_block(miner, block_number):
    random_violation = random.choice(VIOLATIONS)
    score = 1
    if random_violation:
        score = random.randint(10, 30)
    MinerRisk.add_datapoint(miner, score, block_number)
    add_mock_plagued_block(block_number, random_violation)

def add_mock_plagued_block(block_number, violations):
    hash = "0x" + str(block_number)
    current_time_unix = int(time.time())
    return PlaguedBlock.add_test_plagued_block(block_number,
                                               hash,
                                               violations,
                                               current_time_unix,
                                               1)
                                               

@pytest.fixture()
def mock_db(tmp_path):
    # ACTHUNG! We must use real file (no :memory:) here,
    # because FastAPI testing does not work otherwise (threads-related stuff)
    db.bind(provider='sqlite', filename=str(tmp_path / "test.db"), create_db=True)
    db.generate_mapping(create_tables=True)


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app=app)


def test_complete_init_with_default_values(mock_db, client):
    MinerRisk.add_datapoint("abc", 20, 1)
    MinerRisk.add_datapoint("ebf", 30, 2)
    MinerRisk.add_datapoint("ebf", 15, 3)
    MinerRisk.add_datapoint("abc", 20, 4)
    MinerRisk.add_datapoint("abc", 20, 5)
    MinerRisk.add_datapoint("foo", 20, 6)
    response = client.get("/dash/miners")
    assert response.status_code == 200
    assert response.json()['total'] == 3
    # assert response.json() == result

    response = client.get("/dash/miners?order_by=rank&sort_order=asc")
    assert [x['rank'] for x in response.json()['data']] == list(range(3))

    response = client.get("/dash/miners?order_by=rank&sort_order=desc")
    assert [x['rank'] for x in response.json()['data']] == list(reversed(range(3)))

    # Risk score increasing -> rank (standing) increasing
    response = client.get("/dash/miners?order_by=score&sort_order=asc")
    print(response.json())
    assert [x['rank'] for x in response.json()['data']] == list(range(3))

    response = client.get("/dash/miners?order_by=score&sort_order=desc")
    assert [x['rank'] for x in response.json()['data']] == list(reversed(range(3)))



def test_miner_detailed_endpoint(mock_db, client):
    # add mock data 100 times
    for i in range(100):
        add_mock_datapoint_with_mock_block("0x438308", i)
        
    response = client.get("/dash/miners/0x438308")
    assert response.status_code == 200
    assert response.json()['total'] == 50
    
    response = client.get("/dash/miners/0x438308?last_blocks=10")
    assert response.json()['total'] == 10
    
    # Should return 100, because we have only 100 blocks
    response = client.get("/dash/miners/0x438308?last_blocks=101")
    assert response.json()['total'] == 100