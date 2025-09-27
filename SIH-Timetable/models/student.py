from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from enum import Enum

class NotificationPreference(BaseModel):
    email: bool = True
    push: bool = True
    whatsapp: bool = False
    telegram: bool = False
    sms: bool = False

class LearningPreference(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"

class Student(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str
    section_id: str
    semester: int
    notification_preferences: NotificationPreference
    learning_style: Optional[LearningPreference] = None
    attendance_record: Dict[str, List[bool]] = {}  # course_id: [attendance_records]
    location_tracking_enabled: bool = True
