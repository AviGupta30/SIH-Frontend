from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import datetime
import requests
from enum import Enum
import json
import aiohttp
from fastapi.middleware.cors import CORSMiddleware

# Configuration
WEATHER_API_KEY = "8b914716ae0dca0478d13d5a7898da34"  # OpenWeatherMap API key
WEATHER_THRESHOLD = {
    "rain": 25,  # mm of rain
    "temperature": 40,  # Celsius
    "wind": 70,  # km/h
}

# Enhanced Base Models
class WeatherStatus(Enum):
    NORMAL = "normal"
    RAIN = "rain"
    EXTREME_HEAT = "extreme_heat"
    STORM = "storm"

class NotificationPreference(BaseModel):
    email: bool = True
    push: bool = True
    whatsapp: bool = False
    telegram: bool = False
    sms: bool = False

class ResourceStatus(BaseModel):
    room_id: str
    ac_status: bool = False
    projector_status: bool = False
    occupancy: int = 0
    temperature: float = 25.0

class Student(BaseModel):
    id: str
    name: str
    section_id: str
    email: str
    phone: str
    notification_preferences: NotificationPreference
    location_tracking_enabled: bool = True

class AIMessage(BaseModel):
    title: str
    body: str
    priority: int  # 1-5
    type: str  # "schedule_change", "reminder", "emergency", etc.
    actions: Optional[List[Dict[str, str]]]

class AIScheduleAssistant:
    def __init__(self):
        self.personality_types = {
            "formal": {
                "greeting": "Dear {name}",
                "style": "professional and concise"
            },
            "friendly": {
                "greeting": "Hey {name}! 👋",
                "style": "casual and encouraging"
            },
            "motivational": {
                "greeting": "Hello champion! 🌟",
                "style": "energetic and positive"
            }
        }
        
    async def generate_message(self, student: Student, event_type: str, data: dict) -> AIMessage:
        personality = self.personality_types["friendly"]  # Default personality
        
        templates = {
            "schedule_change": {
                "title": "Class Schedule Update",
                "body": f"{personality['greeting']}\n"
                       f"Your {data['subject']} class has been moved:\n"
                       f"From: {data['old_time']}\n"
                       f"To: {data['new_time']}\n"
                       f"Location: {data['location']}\n"
                       f"Reason: {data.get('reason', 'Schedule optimization')}"
            },
            "reminder": {
                "title": "Upcoming Class Reminder",
                "body": f"{personality['greeting']}\n"
                       f"Don't forget your {data['subject']} {data['type']} "
                       f"tomorrow at {data['time']} in {data['location']}."
            },
            "weather_alert": {
                "title": "Weather Impact Alert",
                "body": f"{personality['greeting']}\n"
                       f"Due to {data['weather_condition']}, your class will be "
                       f"{data.get('action', 'conducted online')}."
            }
        }
        
        message = templates.get(event_type)
        if not message:
            raise ValueError(f"Unknown event type: {event_type}")
            
        return AIMessage(
            title=message["title"],
            body=message["body"].format(name=student.name),
            priority=data.get("priority", 3),
            type=event_type,
            actions=data.get("actions", None)
        )

class NotificationManager:
    def __init__(self):
        self.email_config = {}  # Add your email configuration
        self.whatsapp_config = {}  # Add your WhatsApp API configuration
        self.telegram_config = {}  # Add your Telegram bot configuration
        
    async def send_notification(self, student: Student, message: AIMessage):
        tasks = []
        
        if student.notification_preferences.email:
            tasks.append(self.send_email(student.email, message))
        if student.notification_preferences.whatsapp:
            tasks.append(self.send_whatsapp(student.phone, message))
        if student.notification_preferences.telegram:
            tasks.append(self.send_telegram(student.id, message))
            
        await asyncio.gather(*tasks)
        
    async def send_email(self, email: str, message: AIMessage):
        # Implement email sending logic
        pass
        
    async def send_whatsapp(self, phone: str, message: AIMessage):
        # Implement WhatsApp sending logic
        pass
        
    async def send_telegram(self, user_id: str, message: AIMessage):
        # Implement Telegram sending logic
        pass

# Resource Management System
class ResourceManager:
    def __init__(self):
        self.room_status: Dict[str, ResourceStatus] = {}
        
    async def update_room_status(self, room_id: str, status: ResourceStatus):
        self.room_status[room_id] = status
        
    async def optimize_resources(self, room_id: str, class_type: str, occupancy: int):
        status = self.room_status.get(room_id)
        if status:
            # Adjust AC based on occupancy and weather
            if occupancy > 0:
                status.ac_status = True if status.temperature > 25 else False
            else:
                status.ac_status = False
            
            # Adjust projector based on class type
            status.projector_status = class_type in ["lecture", "presentation"]
            
            await self.update_room_status(room_id, status)

# Weather Monitoring System
class WeatherMonitor:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        
    async def check_weather(self, lat: float = 12.9716, lon: float = 77.5946):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    
            weather_status = WeatherStatus.NORMAL
            
            if data.get('rain', {}).get('1h', 0) > WEATHER_THRESHOLD['rain']:
                weather_status = WeatherStatus.RAIN
            if data['main']['temp'] > WEATHER_THRESHOLD['temperature']:
                weather_status = WeatherStatus.EXTREME_HEAT
            if data['wind']['speed'] * 3.6 > WEATHER_THRESHOLD['wind']:
                weather_status = WeatherStatus.STORM
                
            return weather_status
        except Exception as e:
            print(f"Weather API error: {e}")
            return WeatherStatus.NORMAL

# Initialize the applications
app = FastAPI(title="Smart AI-Powered Timetable System")
ai_assistant = AIScheduleAssistant()
notification_manager = NotificationManager()
resource_manager = ResourceManager()
weather_monitor = WeatherMonitor()

# Store student data (replace with database in production)
students: Dict[str, Student] = {}

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, student_id: str):
        await websocket.accept()
        self.active_connections[student_id] = websocket

    def disconnect(self, student_id: str):
        self.active_connections.pop(student_id, None)

    async def send_personal_message(self, message: str, student_id: str):
        if websocket := self.active_connections.get(student_id):
            await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{student_id}")
async def websocket_endpoint(websocket: WebSocket, student_id: str):
    await manager.connect(websocket, student_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time student interactions
            await manager.send_personal_message(f"Message received: {data}", student_id)
    except:
        manager.disconnect(student_id)

@app.post("/student/register")
async def register_student(student: Student):
    students[student.id] = student
    return {"message": "Student registered successfully"}

@app.post("/notify/schedule-change")
async def notify_schedule_change(
    student_id: str,
    subject: str,
    old_time: str,
    new_time: str,
    location: str,
    reason: Optional[str] = None
):
    student = students.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    message = await ai_assistant.generate_message(
        student,
        "schedule_change",
        {
            "subject": subject,
            "old_time": old_time,
            "new_time": new_time,
            "location": location,
            "reason": reason
        }
    )
    
    await notification_manager.send_notification(student, message)
    
    # Send real-time update via WebSocket
    await manager.send_personal_message(
        json.dumps({"type": "schedule_change", "message": message.dict()}),
        student_id
    )
    
    return {"message": "Notification sent successfully"}

# Weather and Resource Management Endpoints
@app.get("/weather/status")
async def get_weather_status():
    status = await weather_monitor.check_weather()
    return {"status": status.value}

@app.post("/room/status")
async def update_room_status(room_id: str, status: ResourceStatus):
    await resource_manager.update_room_status(room_id, status)
    return {"message": "Room status updated successfully"}

@app.get("/room/{room_id}/status")
async def get_room_status(room_id: str):
    status = resource_manager.room_status.get(room_id)
    if not status:
        raise HTTPException(status_code=404, detail="Room not found")
    return status

# Background Tasks
async def monitor_weather_and_adjust_schedule():
    while True:
        weather_status = await weather_monitor.check_weather()
        if weather_status != WeatherStatus.NORMAL:
            # Adjust schedule based on weather
            affected_classes = []  # Get affected classes from timetable
            for class_info in affected_classes:
                if weather_status in [WeatherStatus.STORM, WeatherStatus.EXTREME_HEAT]:
                    # Convert to online class
                    class_info['mode'] = 'online'
                    # Notify affected students
                    await notify_affected_students([{
                        'student_id': class_info['student_id'],
                        'type': 'weather_alert',
                        'data': {
                            'weather_condition': weather_status.value,
                            'action': 'conducted online'
                        }
                    }], BackgroundTasks())
        await asyncio.sleep(1800)  # Check every 30 minutes

# Add this to your existing timetable generation code
async def notify_affected_students(changes: List[dict], background_tasks: BackgroundTasks):
    for change in changes:
        if student := students.get(change['student_id']):
            message = await ai_assistant.generate_message(
                student,
                change['type'],
                change['data']
            )
            background_tasks.add_task(
                notification_manager.send_notification,
                student,
                message
            )

# Start background tasks
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(monitor_weather_and_adjust_schedule())