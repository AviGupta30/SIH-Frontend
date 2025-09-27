from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
import random
import pandas as pd

# --- Database Setup ---
app = Flask(__name__, static_folder='public')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

# --- Database Model ---
class ScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)
    room_name = db.Column(db.String(100), nullable=False)

# --- Data for the Teacher Dashboard ---
teacher_dashboard_data = {
    "teacherName": "Prof. Evelyn", "totalCourses": 6, "totalStudents": 180,
    "classSchedule": [
        {"course": "Linear Algebra", "section": "CS-A", "day": "Monday", "time": "11:00 AM - 12:00 PM", "faculty": "Prof. Evelyn", "room": "C204", "startHour": 11, "durationHours": 1},
        {"course": "Mobile Development", "section": "CS-B", "day": "Monday", "time": "2:00 PM - 3:00 PM", "faculty": "Prof. Evelyn", "room": "Lab 4", "startHour": 14, "durationHours": 1},
        {"course": "Mobile Development", "section": "CS-B", "day": "Monday", "time": "3:00 PM - 4:00 PM", "faculty": "Prof. Evelyn", "room": "Lab 4", "startHour": 15, "durationHours": 1},
        {"course": "Discrete Mathematics", "section": "CS-B", "day": "Tuesday", "time": "10:00 AM - 11:00 AM", "faculty": "Prof. Evelyn", "room": "A201", "startHour": 10, "durationHours": 1},
        {"course": "Calculus II", "section": "MATH-B", "day": "Wednesday", "time": "9:00 AM - 10:00 AM", "faculty": "Prof. Evelyn", "room": "C204", "startHour": 9, "durationHours": 1},
        {"course": "Calculus II", "section": "MATH-B", "day": "Wednesday", "time": "10:00 AM - 11:00 AM", "faculty": "Prof. Evelyn", "room": "C204", "startHour": 10, "durationHours": 1},
        {"course": "Linear Algebra", "section": "CS-A", "day": "Thursday", "time": "9:00 AM - 10:00 AM", "faculty": "Prof. Evelyn", "room": "C204", "startHour": 9, "durationHours": 1},
        {"course": "Advanced Calculus", "section": "MATH-A", "day": "Thursday", "time": "1:00 PM - 2:00 PM", "faculty": "Prof. Evelyn", "room": "C101", "startHour": 13, "durationHours": 1},
        {"course": "Data Structures", "section": "CS-A", "day": "Friday", "time": "10:00 AM - 11:00 AM", "faculty": "Prof. Evelyn", "room": "A101", "startHour": 10, "durationHours": 1},
        {"course": "Data Structures", "section": "CS-A", "day": "Friday", "time": "11:00 AM - 12:00 PM", "faculty": "Prof. Evelyn", "room": "A101", "startHour": 11, "durationHours": 1}
    ],
    "facultyOnLeave": [{"name": "Dr. Brown", "avatar": "https://i.pravatar.cc/32?img=12"}, {"name": "Prof. Johnson", "avatar": "https://i.pravatar.cc/32?img=5"}],
    "weather": { "forecast": [{"day": "Today", "icon": "🌧️", "condition": "Heavy Rain", "recommendation": "Online Classes Recommended", "onlineClassProbability": "90-95%"}, {"day": "Tomorrow", "icon": "☀️", "condition": "Sunny Skies", "recommendation": "Offline Classes as Scheduled", "onlineClassProbability": "<5%"}]}
}

# --- NEW: Data for the Classrooms page ---
teacher_classrooms_data = [
    {"id": "cs-a-la", "name": "Linear Algebra - CS-A", "subject": "Mathematics"},
    {"id": "cs-b-md", "name": "Mobile Development - CS-B", "subject": "Computer Science"},
    {"id": "cs-b-dm", "name": "Discrete Mathematics - CS-B", "subject": "Mathematics"},
    {"id": "math-b-c2", "name": "Calculus II - MATH-B", "subject": "Mathematics"},
    {"id": "math-a-ac", "name": "Advanced Calculus - MATH-A", "subject": "Mathematics"},
    {"id": "cs-a-ds", "name": "Data Structures - CS-A", "subject": "Computer Science"}
]

# --- API Routes ---
@app.route('/api/dashboard')
def get_dashboard_data():
    return jsonify(teacher_dashboard_data)

# --- NEW: API Route for classrooms ---
@app.route('/api/classrooms')
def get_classrooms_data():
    return jsonify(teacher_classrooms_data)

@app.route('/api/upload_excel', methods=['POST'])
def handle_excel_upload():
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
    filename = file.filename
    try:
        if filename.endswith('.csv'): df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')): df = pd.read_excel(file, sheet_name=0)
        else: return jsonify({"error": "Invalid file type. Please upload a CSV or Excel file."}), 400
        df.columns = [col.strip().lower() for col in df.columns]
        required_cols = {'courses', 'weeklyhours', 'faculty', 'rooms'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            return jsonify({"error": f"Missing columns: {', '.join(missing)}"}), 400
        courses_list = []
        for index, row in df.iterrows():
            if pd.notna(row['courses']) and row['courses'] != '' and pd.notna(row['weeklyhours']):
                courses_list.append({'name': str(row['courses']),'hours': int(row['weeklyhours'])})
        faculty_list = df['faculty'].dropna().tolist()
        rooms_list = df['rooms'].dropna().tolist()
        return jsonify({"courses": courses_list, "faculty": faculty_list, "rooms": rooms_list})
    except Exception as e:
        return jsonify({"error": f"Error processing file: {e}"}), 500

def generate_timetable(courses, faculty, rooms):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    # This list now includes the lunch break for display purposes
    time_slots = ['9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM']
    
    schedule = {day: {time: None for time in time_slots} for day in days}
    existing_entries, busy_slots = ScheduleEntry.query.all(), {}
    for entry in existing_entries:
        if entry.faculty_name not in busy_slots: busy_slots[entry.faculty_name] = {}
        if entry.day not in busy_slots[entry.faculty_name]: busy_slots[entry.faculty_name][entry.day] = {}
        busy_slots[entry.faculty_name][entry.day][entry.time_slot] = True
        if entry.room_name not in busy_slots: busy_slots[entry.room_name] = {}
        if entry.day not in busy_slots[entry.room_name]: busy_slots[entry.room_name][entry.day] = {}
        busy_slots[entry.room_name][entry.day][entry.time_slot] = True
    
    course_blocks = []
    for course in courses:
        name, hours = course.get('name'), course.get('hours', 0)
        if name and hours > 0:
            for _ in range(hours):
                course_blocks.append({'name': name, 'duration': 1})

    random.shuffle(course_blocks)
    unplaced_blocks = []
    for block in course_blocks:
        placed = False
        
        # MODIFIED LINE: Filter out the '1:00 PM' slot from the possibilities
        possible_start_slots = [(d, t) for d in days for t in time_slots if t != '1:00 PM']
        random.shuffle(possible_start_slots)

        for day, time in possible_start_slots:
            duration, start_index = block['duration'], time_slots.index(time)
            
            # Check for multi-hour classes crossing the lunch break
            crosses_lunch = False
            for i in range(duration):
                if time_slots[start_index + i] == '1:00 PM':
                    crosses_lunch = True
                    break
            if crosses_lunch: continue

            if start_index + duration > len(time_slots): continue
            if not all(schedule[day][time_slots[start_index + i]] is None for i in range(duration)): continue
            
            possible_faculty = list(faculty)
            random.shuffle(possible_faculty)
            possible_rooms = list(rooms)
            random.shuffle(possible_rooms)
            
            assigned_faculty = None
            assigned_room = None
            
            for f in possible_faculty:
                is_faculty_busy = False
                for i in range(duration):
                    slot_to_check = time_slots[start_index + i]
                    if busy_slots.get(f, {}).get(day, {}).get(slot_to_check):
                        is_faculty_busy = True
                        break
                if not is_faculty_busy:
                    assigned_faculty = f
                    break
            
            for r in possible_rooms:
                is_room_busy = False
                for i in range(duration):
                    slot_to_check = time_slots[start_index + i]
                    if busy_slots.get(r, {}).get(day, {}).get(slot_to_check):
                        is_room_busy = True
                        break
                if not is_room_busy:
                    assigned_room = r
                    break

            if assigned_faculty and assigned_room:
                for i in range(duration):
                    slot_to_fill = time_slots[start_index + i]
                    schedule[day][slot_to_fill] = {"courseName": block['name'], "facultyName": assigned_faculty, "roomName": assigned_room}

                for i in range(duration):
                    slot_to_update = time_slots[start_index + i]
                    if assigned_faculty not in busy_slots: busy_slots[assigned_faculty] = {}
                    if day not in busy_slots[assigned_faculty]: busy_slots[assigned_faculty][day] = {}
                    busy_slots[assigned_faculty][day][slot_to_update] = True
                    if assigned_room not in busy_slots: busy_slots[assigned_room] = {}
                    if day not in busy_slots[assigned_room]: busy_slots[assigned_room][day] = {}
                    busy_slots[assigned_room][day][slot_to_update] = True
                
                placed = True
                break
        
        if not placed:
            unplaced_blocks.append(f"{block['name']}")

    final_unplaced = sorted(list(set(unplaced_blocks)))
    return {"schedule": schedule, "unplaced": final_unplaced}

@app.route('/api/generate', methods=['POST'])
def handle_generate_request():
    data = request.get_json()
    courses, faculty, rooms = data.get('courses', []), data.get('faculty', []), data.get('rooms', [])
    if not all([courses, faculty, rooms]): return jsonify({"error": "Missing required data"}), 400
    result = generate_timetable(courses, faculty, rooms)
    return jsonify(result)

# ... (rest of your Flask app routes) ...
@app.route('/api/saved_schedules')
def get_saved_schedules():
    try:
        schedules = ScheduleEntry.query.all()
        grouped_schedules = {}
        for entry in schedules:
            if entry.section_name not in grouped_schedules: grouped_schedules[entry.section_name] = []
            grouped_schedules[entry.section_name].append({ "day": entry.day, "time_slot": entry.time_slot, "course_name": entry.course_name, "faculty_name": entry.faculty_name, "room_name": entry.room_name })
        return jsonify(grouped_schedules)
    except Exception as e: return jsonify({"error": f"Could not fetch schedules: {e}"}), 500

@app.route('/api/save_schedule', methods=['POST'])
def save_schedule():
    data, section_name = request.get_json(), request.get_json().get('sectionName')
    schedule_data = data.get('schedule')
    if not all([schedule_data, section_name]): return jsonify({"error": "Missing data"}), 400
    try:
        for day, slots in schedule_data.items():
            for time_slot, details in slots.items():
                if details:
                    entry = ScheduleEntry(section_name=section_name, day=day, time_slot=time_slot, course_name=details['courseName'], faculty_name=details['facultyName'], room_name=details['roomName'])
                    db.session.add(entry)
        db.session.commit()
        return jsonify({"message": "Schedule saved successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save: {e}"}), 500
        
@app.route('/api/delete_schedule', methods=['POST'])
def delete_schedule():
    data = request.get_json()
    section_name = data.get('sectionName')
    if not section_name: return jsonify({"error": "Section name is required"}), 400
    try:
        ScheduleEntry.query.filter_by(section_name=section_name).delete()
        db.session.commit()
        return jsonify({"message": f"Schedule for '{section_name}' deleted successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete schedule: {e}"}), 500

@app.route('/api/clear_all_schedules', methods=['POST'])
def clear_all_schedules():
    try:
        db.session.query(ScheduleEntry).delete()
        db.session.commit()
        return jsonify({"message": "All saved schedules have been cleared."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not clear schedules: {e}"}), 500

@app.route('/')
def serve_index(): return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path): return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(port=3000, debug=True)