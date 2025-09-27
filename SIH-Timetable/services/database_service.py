from typing import List, Dict, Any, Optional
from config.database import supabase, TABLES
from models.student import Student
from models.timetable import Course, ClassSchedule
import asyncio

class DatabaseService:
    def __init__(self):
        self.supabase = supabase

    # Student Operations
    async def create_student(self, student: Student) -> Dict:
        try:
            response = self.supabase.table(TABLES["students"]).insert(student.dict()).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to create student: {str(e)}")

    async def get_student(self, student_id: str) -> Optional[Dict]:
        try:
            response = self.supabase.table(TABLES["students"]).select("*").eq("id", student_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            raise Exception(f"Failed to get student: {str(e)}")

    # Course Operations
    async def create_course(self, course: Course) -> Dict:
        try:
            response = self.supabase.table(TABLES["courses"]).insert(course.dict()).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to create course: {str(e)}")

    async def get_courses(self, section_id: str) -> List[Dict]:
        try:
            response = self.supabase.table(TABLES["courses"]).select("*").eq("section_id", section_id).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to get courses: {str(e)}")

    # Schedule Operations
    async def save_schedule(self, schedule: ClassSchedule) -> Dict:
        try:
            response = self.supabase.table(TABLES["schedules"]).insert(schedule.dict()).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to save schedule: {str(e)}")

    async def get_schedule(self, section_id: str, date: str) -> List[Dict]:
        try:
            response = self.supabase.table(TABLES["schedules"]) \
                .select("*") \
                .eq("section_id", section_id) \
                .eq("date", date) \
                .execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to get schedule: {str(e)}")

    # Attendance Operations
    async def mark_attendance(self, student_id: str, schedule_id: str, status: bool) -> Dict:
        try:
            data = {
                "student_id": student_id,
                "schedule_id": schedule_id,
                "status": status,
                "timestamp": "now()"
            }
            response = self.supabase.table(TABLES["attendance"]).insert(data).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to mark attendance: {str(e)}")

    # Weather Log Operations
    async def log_weather(self, weather_data: Dict) -> Dict:
        try:
            response = self.supabase.table(TABLES["weather_logs"]).insert(weather_data).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to log weather: {str(e)}")

    # Notification Operations
    async def save_notification(self, notification_data: Dict) -> Dict:
        try:
            response = self.supabase.table(TABLES["notifications"]).insert(notification_data).execute()
            return response.data[0]
        except Exception as e:
            raise Exception(f"Failed to save notification: {str(e)}")

    # Room Operations
    async def get_available_rooms(self, time_slot: str, date: str) -> List[Dict]:
        try:
            # Complex query to find available rooms
            query = f"""
            SELECT r.* FROM {TABLES['rooms']} r
            WHERE r.id NOT IN (
                SELECT room_id FROM {TABLES['schedules']}
                WHERE date = '{date}' AND time_slot = '{time_slot}'
            )
            """
            response = self.supabase.rpc("get_available_rooms", {
                "p_date": date,
                "p_time_slot": time_slot
            }).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to get available rooms: {str(e)}")

# Create a singleton instance
db = DatabaseService()
