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
    __tablename__ = 'admin_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String)
    expiry = Column(DateTime(timezone=True))


class ClubSwimmer(Base):
    __tablename__ = 'scwr_swimmers'
    id = Column(Integer, primary_key=True)
    sw_id = Column(Integer)
    birth_year = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(Integer) # 0: man, 1: woman

engine = create_engine(db_location_env)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
