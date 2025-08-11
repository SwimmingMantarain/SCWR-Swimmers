from typing import Generator
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from dotenv import load_dotenv
import os

load_dotenv()
db_location_env = os.getenv("DB_LOCATION")
if not db_location_env:
    raise RuntimeError("DB_LOCATION is not set in .env file!!!\n")

Base = declarative_base()

class Token(Base):
    """
    Stores authentication tokens for admin functionality.

    Attributes:
        id (int): Unique primary key.
        token (str): Token secret string.
        expiry (datetime): Expiration datetime of the token (timezone-aware).
    """
    __tablename__ = 'admin_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=False)
    expiry = Column(DateTime(timezone=True), nullable=False)


class ClubSwimmer(Base):
    """
    Stores primary swimmer data for use in `/athletes` endpoint.

    Attributes:
        id (int): Unique primary key.
        sw_id (int): Unique swimmer ID from swimrankings.net.
        birth_year (int): Birth year of the swimmer.
        first_name (str): First name of the swimmer.
        last_name (str): Last name of the swimmer (including middle names).
        gender (int): Gender of the swimmer (0: man, 1: woman).
    """
    __tablename__ = 'scwr_swimmers'

    id = Column(Integer, primary_key=True)
    sw_id = Column(Integer, nullable=False)
    birth_year = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(Integer, nullable=False)  # 0: man, 1: woman

engine = create_engine(db_location_env)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Provides a transactional scope around a series of database operations.

    Yields:
        Session: SQLAlchemy database session.

    Usage:
        This generator is intended to be used with FastAPI dependencies to
        provide a database session that is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
