from enum import Enum
from dataclasses import dataclass
from datetime import datetime, time, date

class Gender(Enum):
    MALE = 0
    FEMALE = 1

@dataclass
class Swimmer:
    sw_id: int
    birth_year: int
    first_name: str
    last_name: str
    gender: Gender

@dataclass
class SwimmerPb:
    sw_style_id: int
    sw_result_id: int
    sw_meet_id: int
    sw_default_fina: str 
    event: str
    course: int
    time: time
    pts: int
    date: date
    city: str
    meet_name: str
    last_scraped: datetime

@dataclass
class Meet:
    startdate: date
    enddate: date
    sw_live_id: int
    sw_id: int
    sw_course: int
    last_updated: datetime
    name: str
    city: str
