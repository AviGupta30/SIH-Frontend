from ortools.sat.python import cp_model
from typing import List, Dict, Optional
import datetime

# Define the data models that were presumably in models.timetable
class Course:
    def __init__(self, id: str, name: str, teacher_id: str, duration: int = 1):
        self.id = id
        self.name = name
        self.teacher_id = teacher_id
        self.duration = duration

class TimeSlot:
    def __init__(self, day: str, start_time: str, end_time: str):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

class ClassSchedule:
    def __init__(self, course_id: str, room_id: str, time_slot: TimeSlot):
        self.course_id = course_id
        self.room_id = room_id
        self.time_slot = time_slot

class Timetable:
    def __init__(self, section_id: str, semester: str, schedules: List[ClassSchedule]):
        self.section_id = section_id
        self.semester = semester
        self.schedules = schedules

class TimetableService:
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        
    def generate_timetable(self, 
                         courses: List[Course],
                         rooms: List[dict],
                         teachers: List[dict],
                         constraints: dict) -> Timetable:
        """
        Generate optimal timetable using constraint programming
        """
        # Initialize variables
        num_days = 5  # Monday to Friday
        slots_per_day = 8  # 8 slots per day
        
        # Create variables - using a more efficient data structure
        assignments = {}
        for course in courses:
            for day in range(num_days):
                for slot in range(slots_per_day):
                    for room in rooms:
                        # Only create variables for valid assignments
                        # Check if room has sufficient capacity for course
                        if room['capacity'] >= getattr(course, 'min_capacity', 0):
                            var_name = f"{course.id}_{day}_{slot}_{room['id']}"
                            assignments[var_name] = self.model.NewBoolVar(var_name)
        
        # Add constraints
        self._add_basic_constraints(assignments, courses, rooms, num_days, slots_per_day)
        self._add_teacher_constraints(assignments, courses, teachers, num_days, slots_per_day)
        self._add_room_constraints(assignments, courses, rooms, num_days, slots_per_day)
        
        # Add objective function (minimize gaps, prioritize certain times, etc.)
        self._add_objective_function(assignments, courses, constraints)
        
        # Solve
        status = self.solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self._create_timetable_from_solution(
                assignments, courses, rooms, num_days, slots_per_day
            )
        else:
            raise ValueError(f"No feasible solution found. Status: {status}")
            
    def _add_basic_constraints(self, assignments, courses, rooms, num_days, slots_per_day):
        """Add basic timetabling constraints"""
        # Each course must be scheduled exactly once
        for course in courses:
            course_vars = []
            for day in range(num_days):
                for slot in range(slots_per_day):
                    for room in rooms:
                        var_name = f"{course.id}_{day}_{slot}_{room['id']}"
                        if var_name in assignments:  # Only consider created variables
                            course_vars.append(assignments[var_name])
            if course_vars:  # Only add constraint if there are variables
                self.model.Add(sum(course_vars) == 1)
                
    def _add_teacher_constraints(self, assignments, courses, teachers, num_days, slots_per_day):
        """Add teacher availability constraints"""
        # Teachers can't be in two places at once
        for teacher in teachers:
            teacher_courses = [c for c in courses if c.teacher_id == teacher['id']]
            for day in range(num_days):
                for slot in range(slots_per_day):
                    teacher_vars = []
                    for course in teacher_courses:
                        for room in rooms:
                            var_name = f"{course.id}_{day}_{slot}_{room['id']}"
                            if var_name in assignments:
                                teacher_vars.append(assignments[var_name])
                    if teacher_vars:
                        self.model.Add(sum(teacher_vars) <= 1)
    
    def _add_room_constraints(self, assignments, courses, rooms, num_days, slots_per_day):
        """Add room availability constraints"""
        # Rooms can't be double-booked
        for room in rooms:
            for day in range(num_days):
                for slot in range(slots_per_day):
                    room_vars = []
                    for course in courses:
                        var_name = f"{course.id}_{day}_{slot}_{room['id']}"
                        if var_name in assignments:
                            room_vars.append(assignments[var_name])
                    if room_vars:
                        self.model.Add(sum(room_vars) <= 1)
    
    def _add_objective_function(self, assignments, courses, constraints):
        """Add objective function to optimize the timetable"""
        # This is a simple example - minimize the number of days with classes
        day_vars = {}
        for var_name in assignments:
            parts = var_name.split('_')
            day = int(parts[1])
            if day not in day_vars:
                day_vars[day] = []
            day_vars[day].append(assignments[var_name])
        
        # Create a variable for each day that is 1 if any class is scheduled that day
        day_has_class = {}
        for day in day_vars:
            day_has_class[day] = self.model.NewBoolVar(f'day_{day}_has_class')
            self.model.AddMaxEquality(day_has_class[day], day_vars[day])
        
        # Minimize the number of days with classes
        self.model.Minimize(sum(day_has_class.values()))
    
    def _create_timetable_from_solution(self, assignments, courses, rooms, num_days, slots_per_day):
        """Create Timetable object from solver solution"""
        schedules = []
        for course in courses:
            for day in range(num_days):
                for slot in range(slots_per_day):
                    for room in rooms:
                        var_name = f"{course.id}_{day}_{slot}_{room['id']}"
                        if var_name in assignments and self.solver.Value(assignments[var_name]) == 1:
                            # Find the course object by ID
                            course_obj = next((c for c in courses if c.id == course.id), None)
                            if course_obj:
                                schedules.append(
                                    ClassSchedule(
                                        course_id=course.id,
                                        room_id=room['id'],
                                        time_slot=TimeSlot(
                                            day=self._day_to_string(day),
                                            start_time=self._slot_to_time(slot),
                                            end_time=self._slot_to_time(slot + course_obj.duration)
                                        )
                                    )
                                )
        return Timetable(
            section_id="CSE-A",  # This should be parameterized
            semester="2023-24-odd",
            schedules=schedules
        )
        
    @staticmethod
    def _slot_to_time(slot: int):
        """Convert slot number to time"""
        # Assuming slots start at 9 AM and each slot is 1 hour
        hour = 9 + slot
        return f"{hour:02d}:00"
        
    @staticmethod
    def _day_to_string(day: int):
        """Convert day number to string"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        return days[day]

# Example usage
if __name__ == "__main__":
    # Sample data
    courses = [
        Course("MATH101", "Mathematics", "T001", 2),
        Course("PHYS101", "Physics", "T002", 1),
        Course("CHEM101", "Chemistry", "T003", 1),
    ]
    
    rooms = [
        {"id": "R101", "capacity": 30},
        {"id": "R102", "capacity": 25},
        {"id": "R201", "capacity": 40},
    ]
    
    teachers = [
        {"id": "T001", "name": "Dr. Smith"},
        {"id": "T002", "name": "Prof. Johnson"},
        {"id": "T003", "name": "Dr. Williams"},
    ]
    
    constraints = {
        "max_classes_per_day": 4,
        "preferred_times": ["09:00", "10:00", "11:00"]
    }
    
    # Generate timetable
    service = TimetableService()
    try:
        timetable = service.generate_timetable(courses, rooms, teachers, constraints)
        print("Timetable generated successfully!")
        for schedule in timetable.schedules:
            print(f"Course: {schedule.course_id}, Room: {schedule.room_id}, "
                  f"Day: {schedule.time_slot.day}, Time: {schedule.time_slot.start_time}-{schedule.time_slot.end_time}")
    except ValueError as e:
        print(f"Error: {e}")