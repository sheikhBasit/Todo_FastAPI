import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import URL, make_url
from .config import settings

# 1. Get the URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 2. Create the Engine
# Note: Since you are using Neon (Serverless), it's often good to add 
# pool_pre_ping=True to handle connection drops automatically.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True
)

# 3. Setup the Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Setup the Base class for models
class Base(DeclarativeBase):
    pass
# 5. Connection Listener (Corrected)
@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    print("✅ Database Connection Successful!")

# 6. Dependency to get the DB session in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Optional: Immediate connection test on startup (helpful for debugging)
try:
    with engine.connect() as conn:
        print(f"🚀 Engine initialized for host: {engine.url.host}")
except Exception as e:
    print(f"❌ Initial engine connection failed: {e}")