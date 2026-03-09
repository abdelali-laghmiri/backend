from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.settings import settings

# =====================================================
# Database Session
# Provides the SQLAlchemy engine and per-request sessions.
# =====================================================

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Yield a database session and guarantee cleanup after request handling."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
