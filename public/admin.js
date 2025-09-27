document.addEventListener('DOMContentLoaded', () => {
    
    // --- THEME SWITCHER LOGIC ---
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    const applySavedTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-theme');
            if(themeToggle) themeToggle.checked = true;
        } else {
            body.classList.remove('dark-theme');
            if(themeToggle) themeToggle.checked = false;
        }
    };

    if(themeToggle){
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                body.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }
        });
    }
    applySavedTheme();
    // --- END THEME SWITCHER LOGIC ---


    const dashboardApiUrl = 'http://localhost:3000/api/dashboard';
    const classroomsApiUrl = 'http://localhost:3000/api/classrooms'; // New API URL

    // --- DOM References ---
    const teacherNameEl = document.getElementById('teacher-name');
    const totalCoursesEl = document.getElementById('totalCourses');
    const totalStudentsEl = document.getElementById('totalStudents');
    const facultyOnLeaveList = document.getElementById('facultyOnLeaveList');
    const forecastContainerEl = document.getElementById('forecastContainer');
    const scheduleGridEl = document.getElementById('schedule-grid');
    
    // NEW: View and Navigation DOM references
    const navLinks = document.querySelectorAll('#sidebar-nav li');
    const viewContainers = document.querySelectorAll('.view-container');
    const classroomGridEl = document.getElementById('classroom-grid');
    const backToClassroomsBtn = document.getElementById('back-to-classrooms-btn');
    const detailClassroomNameEl = document.getElementById('detail-classroom-name');
    
    const TIMETABLE_START_HOUR = 8;
    const TIMETABLE_END_HOUR = 18;
    const NUM_HOURS = TIMETABLE_END_HOUR - TIMETABLE_START_HOUR;
    const NUM_DAYS = 5;


    // --- NEW: VIEW SWITCHING LOGIC ---
    function switchView(viewId) {
        viewContainers.forEach(container => {
            container.classList.remove('active');
        });
        navLinks.forEach(link => {
            link.classList.remove('active');
        });

        const targetView = document.getElementById(viewId);
        if (targetView) {
            targetView.classList.add('active');
        }

        const targetLink = document.querySelector(`#sidebar-nav li[data-view="${viewId}"]`);
        if (targetLink) {
            targetLink.classList.add('active');
        }
    }

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const viewId = link.getAttribute('data-view');
            if (viewId) {
                switchView(viewId);
                // If we are switching to the classroom list view, fetch the data
                if (viewId === 'classroom-list-view') {
                    fetchAndDisplayClassrooms();
                }
            }
        });
    });
    
    if (backToClassroomsBtn) {
        backToClassroomsBtn.addEventListener('click', () => {
            switchView('classroom-list-view');
        });
    }
    // --- END NEW VIEW SWITCHING LOGIC ---


    // --- TIMETABLE LOGIC (Your existing code, unchanged) ---
    function setupTimetableGrid() {
        if (!scheduleGridEl) return;
        scheduleGridEl.innerHTML = ''; 

        const originCell = document.createElement('div');
        originCell.style.gridRow = '1';
        originCell.style.gridColumn = '1';
        scheduleGridEl.appendChild(originCell);

        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        days.forEach((day, index) => {
            const header = document.createElement('div');
            header.className = 'day-header';
            header.textContent = day;
            header.style.gridRow = '1';
            header.style.gridColumn = `${index + 2}`;
            scheduleGridEl.appendChild(header);
        });
        
        for (let i = 0; i < NUM_HOURS; i++) {
            const hour = TIMETABLE_START_HOUR + i;
            const timeLabel = document.createElement('div');
            timeLabel.className = 'time-slot';
            timeLabel.textContent = `${hour % 12 === 0 ? 12 : hour % 12}:00 ${hour < 12 ? 'AM' : 'PM'}`;
            timeLabel.style.gridRow = `${i + 2}`;
            timeLabel.style.gridColumn = '1';
            scheduleGridEl.appendChild(timeLabel);

            for (let j = 0; j < NUM_DAYS; j++) {
                const bgCell = document.createElement('div');
                bgCell.className = 'grid-cell-bg';
                bgCell.style.gridRow = `${i + 2}`;
                bgCell.style.gridColumn = `${j + 2}`;
                scheduleGridEl.appendChild(bgCell);
            }
        }
    }

    function populateTimetable(classSchedule) {
        if (!scheduleGridEl) return;
        scheduleGridEl.querySelectorAll('.class-card').forEach(card => card.remove());
        const dayMapping = { Monday: 2, Tuesday: 3, Wednesday: 4, Thursday: 5, Friday: 6 };
        
        classSchedule.forEach(cls => {
            if (typeof cls.startHour !== 'number' || typeof cls.durationHours !== 'number') return;
            const dayCol = dayMapping[cls.day];
            if (dayCol === undefined) return;
            
            const rowStart = (cls.startHour - TIMETABLE_START_HOUR) + 2;
            const rowEnd = rowStart + cls.durationHours;

            const classCard = document.createElement('div');
            classCard.className = 'class-card';
            classCard.style.gridRow = `${rowStart} / ${rowEnd}`;
            classCard.style.gridColumn = `${dayCol}`;
            
            classCard.innerHTML = `
                <div class="course-name" title="${cls.course}">${cls.course}</div>
                <div class="details">
                    <span>${cls.time}</span>
                    <span>Section: ${cls.section}</span>
                    <span>Room: ${cls.room}</span>
                </div>
            `;
            scheduleGridEl.appendChild(classCard);
        });
    }
    // --- END TIMETABLE LOGIC ---


    // --- DATA FETCHING LOGIC ---
    async function fetchDashboardData() {
        try {
            const response = await fetch(dashboardApiUrl);
            if (!response.ok) { throw new Error(`HTTP error! Status: ${response.status}`); }
            const data = await response.json();

            if(teacherNameEl) teacherNameEl.textContent = data.teacherName;
            if(totalCoursesEl) totalCoursesEl.textContent = data.totalCourses;
            if(totalStudentsEl) totalStudentsEl.textContent = data.totalStudents;

            if(facultyOnLeaveList) {
                facultyOnLeaveList.innerHTML = '';
                data.facultyOnLeave.forEach(({ name, avatar }) => {
                    const li = document.createElement('li');
                    li.innerHTML = `<div class="info"><img src="${avatar}" alt="${name}" /><span>${name}</span></div><span class="leave-status">On Leave</span>`;
                    facultyOnLeaveList.appendChild(li);
                });
            }

            if (forecastContainerEl && data.weather && data.weather.forecast) {
                forecastContainerEl.innerHTML = '';
                data.weather.forecast.forEach(dayForecast => {
                    const forecastCard = document.createElement('div');
                    forecastCard.className = `forecast-card ${dayForecast.day === 'Today' && dayForecast.recommendation.includes('Online') ? 'is-alert' : ''}`;
                    forecastCard.innerHTML = `<div class="day">${dayForecast.day}</div><div class="icon">${dayForecast.icon}</div><div class="condition">${dayForecast.condition}</div><div class="recommendation">${dayForecast.recommendation}</div><div class="probability">Online Class Probability: <strong>${dayForecast.onlineClassProbability}</strong></div>`;
                    forecastContainerEl.appendChild(forecastCard);
                });
            }
            populateTimetable(data.classSchedule);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
            if (scheduleGridEl) {
                scheduleGridEl.innerHTML = `<div style="color: #ff4d4d; padding: 2rem; text-align: center; background: rgba(255,0,0,0.1); border: 1px solid #ff4d4d;"><strong>Connection Error</strong><p>Could not load schedule data.</p></div>`;
            }
        }
    }

    // --- NEW: CLASSROOM FETCHING AND DISPLAY LOGIC ---
    let classroomsLoaded = false;
    async function fetchAndDisplayClassrooms() {
        if (classroomsLoaded || !classroomGridEl) return; // Don't fetch again if already loaded
        
        try {
            const response = await fetch(classroomsApiUrl);
            if (!response.ok) { throw new Error(`HTTP error! Status: ${response.status}`); }
            const classrooms = await response.json();
            
            classroomGridEl.innerHTML = ''; // Clear previous
            
            classrooms.forEach(classroom => {
                const card = document.createElement('div');
                card.className = 'classroom-card';
                card.innerHTML = `
                    <div class="classroom-card-name">${classroom.name}</div>
                    <div class="classroom-card-subject">${classroom.subject}</div>
                `;
                card.addEventListener('click', () => {
                    if (detailClassroomNameEl) {
                        detailClassroomNameEl.textContent = classroom.name;
                    }
                    switchView('classroom-detail-view');
                });
                classroomGridEl.appendChild(card);
            });
            
            classroomsLoaded = true; // Mark as loaded
        } catch (error) {
            console.error('Failed to fetch classroom data:', error);
            if (classroomGridEl) {
                classroomGridEl.innerHTML = `<p style="color: #ff4d4d;">Could not load classroom data.</p>`;
            }
        }
    }


    // --- INITIALIZATION ---
    setupTimetableGrid();
    fetchDashboardData();
    // switchView('main-dashboard-view'); // Explicitly set the initial view
});