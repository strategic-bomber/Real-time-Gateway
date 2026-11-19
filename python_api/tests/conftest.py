import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import python_api.db as db
import routers.auth
import routers.deals
import routers.fields
import routers.messages
from python_api.db import Base, Deal, DealMember, DealField
from python_api.main import app

TEST_DB_URL = "sqlite:///python_api/tests/test_deal_data.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# !!! Š‹—…‚‰ ”ˆŠ‘: ®¤¬¥­ï¥¬ SessionLocal ‚…‡„…, £¤¥ ®­ ¡ë« ¨¬¯®àâ¨à®¢ ­
db.SessionLocal = TestSession
routers.auth.SessionLocal = TestSession
routers.deals.SessionLocal = TestSession
routers.fields.SessionLocal = TestSession
routers.messages.SessionLocal = TestSession

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    session = TestSession()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db_session):
    with TestClient(app) as c:
        yield c

@pytest.fixture
def seed_deal(db_session):
    deal = Deal(id="deal-42", status="draft", revision=1)
    db_session.add(deal)
    db_session.add(DealMember(deal_id="deal-42", user_id="client1", role="client"))
    db_session.add(DealMember(deal_id="deal-42", user_id="manager1", role="manager"))
    
    for name in ["horsePower", "engineVolume", "paintColour"]:
        db_session.add(DealField(deal_id="deal-42", field_name=name, value="", status="pending", version=1))
    
    db_session.commit()
    return deal

def get_token(client, username, deal_id="deal-42"):
    res = client.post("/api/demo/sessions", json={"username": username, "deal_id": deal_id})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["token"]