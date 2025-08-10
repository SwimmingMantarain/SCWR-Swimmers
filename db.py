from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from dotenv import load_dotenv
import os

load_dotenv()
db_location_env = os.getenv("DB_LOCATION")
if not db_location_env:
    raise RuntimeError("DB_LOCATION is not set in .env file!!!\n")
db_location = db_location_env

Base = declarative_base()

class Token(Base):
    __tablename__ = 'admin_tokens'
    id = Column(Integer, primary_key=True)
    token = Column(String)
    expiry = Column(DateTime)


class ClubSwimmer(Base):
    __tablename__ = 'scwr_swimmers'
    id = Column(Integer, primary_key=True)
    sw_id = Column(Integer)
    birth_year = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(Integer) # 0: man, 1: woman

class DB:
    def __init__(self): 
        self.engine = create_engine(db_location)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add(self, object: ClubSwimmer | Token | None = None):
        if not object:
            raise ValueError("[DB ERROR]: `Object to add not provided!`\n")

        self.session.add(object)

    def rm(self, object: ClubSwimmer | Token | None = None):
        if not object:
            raise ValueError("[DB ERROR]: `Object to remove not provided!\n")
        self.session.delete(object)

    def query(self, type: type[ClubSwimmer | Token] | None = None) :
        return self.session.query(type)

db = DB()
