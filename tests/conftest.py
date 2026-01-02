import sys
from pathlib import Path
import pytest
import asyncio
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.config.database import Base, get_db
from app.main import app
from app.models import model as models
from app.utils import auth

# 1. Setup in-memory SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable Foreign Key support for SQLite (important for Task -> Group relations)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, item):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
async def client(db_session):
    """A basic client for testing Auth routes (register/login)"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def auth_client(client, db_session):
    """
    A client that comes pre-authenticated with a test user.
    Use this for testing Groups and Tasks.
    """
    # 1. Create a test user directly in DB
    user_data = {"username": "testuser", "email": "test@example.com"}
    hashed_pwd = auth.get_password_hash("password123")
    test_user = models.User(**user_data, password_hash=hashed_pwd)
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # 2. Generate a token
    access_token = auth.create_access_token(data={"sub": test_user.username})
    
    # 3. Add token to client headers
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    # 4. Attach user object to the client so tests can reference its ID (e.g., client.user.id)
    client.user = test_user
    
    return client