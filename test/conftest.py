from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, RootTransaction, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from src.dependencies import get_db
from src.main import app
from src.models import Base

# In-memory database
# Preferably the tests would use postgres, same as 'prod'. But actually is it that important?
# These test functionality of the application, the 'contract' with the database is that is performs all the operations successfully or throws otherwise, no matter the configuration.
# Also the layer of sqlalchemy exists and provides even further abstraction where (to my knowledge) there are no differences between different dbs at that level (apart from config)
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine: Engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, Any, None]:
    connection: Connection = engine.connect()
    transaction: RootTransaction = connection.begin()

    db: Session = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)
