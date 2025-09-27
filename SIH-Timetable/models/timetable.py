from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time

class Course(BaseModel):
    id: str
    name: str
    teacher_id: str
    credits: int
    has_lab: bool = False
    can_be_online: bool = False

class TimeSlot(BaseModel):
    start_time: time
    end_time: time
    day: str

class ClassSchedule(BaseModel):
    id: str
    course_id: str
    room_id: str
    time_slot: TimeSlot
    is_online: bool = False
    mode: str = "in_person"  # in_person, online, hybrid

class Timetable(BaseModel):
    section_id: str
    semester: str
    schedules: List[ClassSchedule]
    last_updated: datetime = datetime.now()
