from typing import Generator
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy import Date, ForeignKey, create_engine, Column, Integer, String, DateTime, Time
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
    Stores primary swimmer data for use in `/athletes` & `/athlete?id=?` endpoints.

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
    pbs = relationship('ClubSwimmerPb', back_populates='athlete')

class ClubSwimmerPb(Base):
    """
    Stores the pbs of a ClubSwimmer scraped from swimrankings.net

    Atributes:
        id (int): Unique primary key
        athlete_id (int): Foreign key to the swimmmer in `scwr_swimmers` this PB belongs to.
        sw_style_id (int): Unique style ID from swimrankings.net
        sw_result_id (int): Unique race result ID from swimrankings.net
        sw_meet_id (int): Unique meet ID from swimrankings.net
        sw_default_fina (str): Default scoring used by swimrankings.net when this was scraped (As of development its FINA 2024)
        event (str): String of the event (distance(m) stroke)
        course (int): Course length in meters (0 for 25m meters, 1 for 50m)
        time (Time): The PB time
        pts (int): FINA points based on the default swimrankings.net used
        date (Date): Date of the pb.
        city (str): The name of the city the pb was swam in.
        meet_name (str): The name of the meet at which the pb was swum.
        last_scraped (DateTime): The time and date the last time this pb was scraped for.
    """
    __tablename__ = 'athlete_pbs'

    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('scwr_swimmers.id'), nullable=False)
    sw_style_id = Column(Integer, nullable=False)
    sw_result_id = Column(Integer, nullable=False)
    sw_meet_id = Column(Integer, nullable=False)
    sw_default_fina = Column(String, nullable=False)
    event = Column(String, nullable=False)
    course = Column(Integer, nullable=False)
    time = Column(Time, nullable=False)
    pts = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    meet_name = Column(String, nullable=False)
    last_scraped = Column(DateTime(timezone=True), nullable=False)

    athlete = relationship('ClubSwimmer', back_populates='pbs')

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
