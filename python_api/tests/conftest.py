import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# 1. Точное определение всех уровней папок
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))       # .../python_api/tests
PYTHON_API_DIR = os.path.dirname(CURRENT_DIR)                  # .../python_api
PROJECT_ROOT = os.path.dirname(PYTHON_API_DIR)                 # .../Real-time-Gateway (корень)

# 2. Добавляем ОБА пути: корень (для routers) и python_api (для db, main)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if PYTHON_API_DIR not in sys.path:
    sys.path.insert(0, PYTHON_API_DIR)

# 3. Теперь импорты сработают корректно
import db
import python_api.routers.auth
import python_api.routers.deals
import python_api.routers.fields
import python_api.routers.messages
from db import Base, Deal, DealMember, DealField
from main import app

# 4. Абсолютный путь к тестовой БД (остаётся без изменений)
TEST_DB_URL = f"sqlite:///{os.path.join(PYTHON_API_DIR, 'test_deal_data.db')}"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# 5. Подмена SessionLocal везде
db.SessionLocal = TestSession
python_api.routers.auth.SessionLocal = TestSession
python_api.routers.deals.SessionLocal = TestSession
python_api.routers.fields.SessionLocal = TestSession
python_api.routers.messages.SessionLocal = TestSession

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