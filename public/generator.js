document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const outputDiv = document.getElementById('timetable-output');
    const outputControlsDiv = document.getElementById('output-controls');
    const generateBtn = document.querySelector('.generate-btn');
    const addCourseBtn = document.getElementById('add-course-btn');
    const coursesListDiv = document.getElementById('courses-list');
    const addFacultyBtn = document.getElementById('add-faculty-btn');
    const facultyListDiv = document.getElementById('faculty-list');
    const addRoomBtn = document.getElementById('add-room-btn');
    const roomsListDiv = document.getElementById('rooms-list');
    const excelUploadInput = document.getElementById('excel-upload');
    const fileNameSpan = document.getElementById('file-name');
    const modal = document.getElementById('saved-schedules-modal');
    const viewSavedBtn = document.getElementById('view-saved-btn');
    const modalCloseBtn = document.querySelector('.modal-close');
    const savedSchedulesContentDiv = document.getElementById('saved-schedules-content');
    const clearAllBtn = document.getElementById('clear-all-btn');

    let lastGeneratedSchedule = null;
    let courseColorMap = new Map();
    let nextColorIndex = 1;

    function addCourseRow(name = '', hours = '') {
        const newCourseGroup = document.createElement('div');
        newCourseGroup.className = 'course-input-group';
        newCourseGroup.innerHTML = `<input type="text" class="course-name" placeholder="Course Name" value="${name}" /><input type="number" class="course-hours" placeholder="Hrs/Wk" min="1" max="10" value="${hours}" />`;
        coursesListDiv.appendChild(newCourseGroup);
    }
    
    function addSingleInputRow(container, value = '', placeholder = '') {
        const newInputGroup = document.createElement('div');
        newInputGroup.className = 'list-input-group';
        newInputGroup.innerHTML = `<input type="text" placeholder="New ${placeholder}" value="${value}" />`;
        container.appendChild(newInputGroup);
    }
    
    function resetForm() {
        document.getElementById('section-name').value = '';
        fileNameSpan.textContent = 'No file chosen';
        excelUploadInput.value = null;
        coursesListDiv.innerHTML = '';
        facultyListDiv.innerHTML = '';
        roomsListDiv.innerHTML = '';
        addCourseRow();
        addSingleInputRow(facultyListDiv, '', 'Faculty');
        addSingleInputRow(roomsListDiv, '', 'Room');
        courseColorMap.clear();
        nextColorIndex = 1;
    }

    addCourseBtn.addEventListener('click', () => addCourseRow());
    addFacultyBtn.addEventListener('click', () => addSingleInputRow(facultyListDiv, '', 'Faculty'));
    addRoomBtn.addEventListener('click', () => addSingleInputRow(roomsListDiv, '', 'Room'));
    
    function populateFormWithData(data) {
        coursesListDiv.innerHTML = ''; facultyListDiv.innerHTML = ''; roomsListDiv.innerHTML = '';
        if (data.courses && data.courses.length > 0) {
            data.courses.forEach(course => addCourseRow(course.name, course.hours));
        } else { addCourseRow(); }
        if (data.faculty && data.faculty.length > 0) {
            data.faculty.forEach(name => addSingleInputRow(facultyListDiv, name, 'Faculty'));
        } else { addSingleInputRow(facultyListDiv, '', 'Faculty'); }
        if (data.rooms && data.rooms.length > 0) {
            data.rooms.forEach(name => addSingleInputRow(roomsListDiv, name, 'Room'));
        } else { addSingleInputRow(roomsListDiv, '', 'Room'); }
    }

    excelUploadInput.addEventListener('change', async () => {
        const file = excelUploadInput.files[0]; if (!file) {fileNameSpan.textContent = 'No file chosen'; return;} 
        fileNameSpan.textContent = `Uploading: ${file.name}`; 
        const formData = new FormData(); 
        formData.append('file', file); 
        try {
            const response = await fetch('/api/upload_excel', {method: 'POST', body: formData,}); 
            if (!response.ok) {const errorData = await response.json(); throw new Error(errorData.error || 'Failed to upload file');} 
            const data = await response.json(); 
            populateFormWithData(data); 
            fileNameSpan.textContent = `Successfully loaded: ${file.name}`;
        } catch (error) {
            console.error('Error uploading file:', error); 
            fileNameSpan.textContent = `Error: ${error.message}`;
        }
    });

    addCourseRow();
    addSingleInputRow(facultyListDiv, '', 'Faculty');
    addSingleInputRow(roomsListDiv, '', 'Room');
    
    function renderGridTimetable(scheduleData, unplaced = []) {
        outputDiv.innerHTML = '';
        const gridContainer = document.createElement('div');
        gridContainer.className = 'schedule-grid';

        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        // MODIFIED: This array now includes 1:00 PM to ensure the row is rendered
        const timeSlots = ['9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM'];
        
        gridContainer.appendChild(document.createElement('div')); 
        days.forEach(day => {
            const dayHeader = document.createElement('div');
            dayHeader.className = 'day-header';
            dayHeader.textContent = day;
            gridContainer.appendChild(dayHeader);
        });
        timeSlots.forEach(time => {
            const timeSlot = document.createElement('div');
            timeSlot.className = 'time-slot';
            timeSlot.textContent = time;
            gridContainer.appendChild(timeSlot);
        });

        for (let r = 0; r < timeSlots.length; r++) {
            for (let c = 0; c < days.length; c++) {
                const bgCell = document.createElement('div');
                bgCell.className = 'grid-cell-bg';
                bgCell.style.gridRow = `${r + 2}`;
                bgCell.style.gridColumn = `${c + 2}`;
                gridContainer.appendChild(bgCell);
            }
        }

        const placedCells = new Set();
        timeSlots.forEach((time, timeIndex) => {
            days.forEach((day, dayIndex) => {
                const cellKey = `${day}-${time}`;
                if (placedCells.has(cellKey)) return;

                const classDetails = scheduleData[day]?.[time];
                if (classDetails) {
                    let duration = 1;
                    for (let i = timeIndex + 1; i < timeSlots.length; i++) {
                        const nextTime = timeSlots[i];
                        const nextClass = scheduleData[day]?.[nextTime];
                        if (nextClass && nextClass.courseName === classDetails.courseName && nextClass.facultyName === classDetails.facultyName && nextClass.roomName === classDetails.roomName) {
                            duration++;
                            placedCells.add(`${day}-${nextTime}`);
                        } else {
                            break;
                        }
                    }
                    
                    if (!courseColorMap.has(classDetails.courseName)) {
                        courseColorMap.set(classDetails.courseName, nextColorIndex);
                        nextColorIndex = (nextColorIndex % 5) + 1;
                    }
                    const colorIndex = courseColorMap.get(classDetails.courseName);

                    const classCard = document.createElement('div');
                    classCard.className = `class-card color-${colorIndex}`;
                    classCard.style.gridRow = `${timeIndex + 2} / span ${duration}`;
                    classCard.style.gridColumn = `${dayIndex + 2}`;
                    classCard.innerHTML = `<div class="course-name">${classDetails.courseName}</div><div class="details">${classDetails.facultyName}<br>${classDetails.roomName}</div>`;
                    gridContainer.appendChild(classCard);
                    placedCells.add(cellKey);
                }
            });
        });

        outputDiv.appendChild(gridContainer);

        if (unplaced && unplaced.length > 0) {
            const unplacedInfo = document.createElement('p');
            unplacedInfo.style.cssText = 'margin-top: 1rem; color: #ff5555;';
            unplacedInfo.textContent = `Could not place: ${unplaced.join(', ')}`;
            outputDiv.appendChild(unplacedInfo);
        }
    }


    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        courseColorMap.clear();
        nextColorIndex = 1;

        generateBtn.textContent = 'Generating...';
        generateBtn.disabled = true;
        outputControlsDiv.innerHTML = '';
        outputDiv.innerHTML = `<div class="placeholder">🧠 Running scheduling algorithm...</div>`;
        const sectionName = document.getElementById('section-name').value.trim();
        const courseInputs = document.querySelectorAll('.course-input-group');
        const courses = [];
        courseInputs.forEach(group => { const name = group.querySelector('.course-name').value.trim(); const hours = parseInt(group.querySelector('.course-hours').value, 10); if (name && hours > 0) courses.push({ name, hours }); });
        const getValuesFromList = (listId) => { const values = []; document.querySelectorAll(`#${listId} input`).forEach(input => { const value = input.value.trim(); if (value) values.push(value); }); return values; };
        const faculty = getValuesFromList('faculty-list');
        const rooms = getValuesFromList('rooms-list');
        if (!sectionName || courses.length === 0 || faculty.length === 0 || rooms.length === 0) {
            outputDiv.innerHTML = `<div class="placeholder">Please fill out all fields, including Section Name.</div>`;
            generateBtn.textContent = 'Generate Timetable';
            generateBtn.disabled = false;
            return;
        }
        try {
            const response = await fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ courses, faculty, rooms }), });
            if (!response.ok) { throw new Error(`Server responded with status: ${response.status}`); }
            const result = await response.json();
            lastGeneratedSchedule = result.schedule;
            
            renderGridTimetable(result.schedule, result.unplaced);
            
            const saveBtn = document.createElement('button');
            saveBtn.textContent = 'Save This Timetable';
            saveBtn.className = 'generate-btn';
            saveBtn.style.marginBottom = '20px';
            outputControlsDiv.appendChild(saveBtn);
            
            saveBtn.addEventListener('click', async () => {
                if (confirm("Do you really want to save this timetable? This cannot be undone.")) {
                    saveBtn.textContent = 'Saving...';
                    saveBtn.disabled = true;
                    try {
                        const saveResponse = await fetch('/api/save_schedule', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ schedule: lastGeneratedSchedule, sectionName: sectionName }), });
                        const saveResult = await saveResponse.json();
                        if (!saveResponse.ok) throw new Error(saveResult.error);
                        const successMsg = document.createElement('p');
                        successMsg.textContent = saveResult.message;
                        successMsg.style.color = 'lime';
                        successMsg.style.textAlign = 'center';
                        successMsg.style.marginBottom = '10px';
                        outputControlsDiv.innerHTML = '';
                        outputControlsDiv.appendChild(successMsg);
                        resetForm();
                    } catch (error) {
                        alert('Could not save schedule: ' + error.message);
                        saveBtn.textContent = 'Save This Timetable';
                        saveBtn.disabled = false;
                    }
                }
            });
        } catch (error) {
            outputDiv.innerHTML = `<div class="placeholder" style="color: #ff5555;">An error occurred.</div>`;
            console.error('Error generating timetable:', error);
        } finally {
            generateBtn.textContent = 'Generate Timetable';
            generateBtn.disabled = false;
        }
    });

    const fetchAndDisplaySavedSchedules = async () => {
        savedSchedulesContentDiv.innerHTML = '<p>Loading saved schedules...</p>';
        try {
            const response = await fetch('/api/saved_schedules');
            const data = await response.json();
            if (Object.keys(data).length === 0) { savedSchedulesContentDiv.innerHTML = '<p>No schedules have been saved yet.</p>'; return; }
            let html = '';
            const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
            const timeSlots = ['9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM'];
            for (const sectionName in data) {
                const scheduleGrid = {};
                data[sectionName].forEach(entry => { 
                    if (!scheduleGrid[entry.day]) scheduleGrid[entry.day] = {}; 
                    scheduleGrid[entry.day][entry.time_slot] = { 
                        courseName: entry.course_name, 
                        facultyName: entry.faculty_name, 
                        roomName: entry.room_name 
                    }; 
                });
                html += `<div class="saved-section" data-section="${sectionName}"><div class="saved-section-header"><span>${sectionName}</span><button class="delete-schedule-btn" data-section="${sectionName}">Delete</button></div><div class="saved-timetable-details">`;
                
                const savedScheduleContainer = document.createElement('div');
                savedScheduleContainer.className = 'schedule-grid';

                savedScheduleContainer.appendChild(document.createElement('div')); 
                days.forEach(day => {
                    const dayHeader = document.createElement('div');
                    dayHeader.className = 'day-header';
                    dayHeader.textContent = day;
                    savedScheduleContainer.appendChild(dayHeader);
                });
                timeSlots.forEach(time => {
                    const timeSlot = document.createElement('div');
                    timeSlot.className = 'time-slot';
                    timeSlot.textContent = time;
                    savedScheduleContainer.appendChild(timeSlot);
                });

                for (let r = 0; r < timeSlots.length; r++) {
                    for (let c = 0; c < days.length; c++) {
                        const bgCell = document.createElement('div');
                        bgCell.className = 'grid-cell-bg';
                        bgCell.style.gridRow = `${r + 2}`;
                        bgCell.style.gridColumn = `${c + 2}`;
                        savedScheduleContainer.appendChild(bgCell);
                    }
                }

                const placedCellsForSaved = new Set();
                let savedCourseColorMap = new Map();
                let savedNextColorIndex = 1;

                timeSlots.forEach((time, timeIndex) => {
                    days.forEach((day, dayIndex) => {
                        const currentCellKey = `${day}-${time}`;
                        if (placedCellsForSaved.has(currentCellKey)) {
                            return;
                        }

                        const classDetails = scheduleGrid[day]?.[time];

                        if (classDetails) {
                            let duration = 1;
                            for (let i = timeIndex + 1; i < timeSlots.length; i++) {
                                const nextTime = timeSlots[i];
                                const nextClassDetails = scheduleGrid[day]?.[nextTime];
                                if (nextClassDetails && 
                                    nextClassDetails.courseName === classDetails.courseName &&
                                    nextClassDetails.facultyName === classDetails.facultyName &&
                                    nextClassDetails.roomName === classDetails.roomName) {
                                    duration++;
                                    placedCellsForSaved.add(`${day}-${nextTime}`);
                                } else {
                                    break;
                                }
                            }

                            if (!savedCourseColorMap.has(classDetails.courseName)) {
                                savedCourseColorMap.set(classDetails.courseName, savedNextColorIndex);
                                savedNextColorIndex = (savedNextColorIndex % 5) + 1;
                            }
                            const colorIndex = savedCourseColorMap.get(classDetails.courseName);

                            const classCard = document.createElement('div');
                            classCard.className = `class-card color-${colorIndex}`;
                            classCard.style.gridRow = `${timeIndex + 2} / span ${duration}`;
                            classCard.style.gridColumn = `${dayIndex + 2}`;
                            classCard.innerHTML = `
                                <div class="course-name">${classDetails.courseName}</div>
                                <div class="details">${classDetails.facultyName}<br>${classDetails.roomName}</div>
                            `;
                            savedScheduleContainer.appendChild(classCard);
                            placedCellsForSaved.add(currentCellKey);
                        }
                    });
                });

                html += savedScheduleContainer.outerHTML;
                html += '</div></div>';
            }
            savedSchedulesContentDiv.innerHTML = html;
        } catch (error) {
            savedSchedulesContentDiv.innerHTML = '<p style="color:red;">Could not load saved schedules.</p>';
            console.error(error);
        }
    };
    
    viewSavedBtn.addEventListener('click', () => { fetchAndDisplaySavedSchedules(); modal.style.display = 'block'; });
    modalCloseBtn.addEventListener('click', () => { modal.style.display = 'none'; });
    window.addEventListener('click', (event) => { if (event.target == modal) { modal.style.display = 'none'; } });
    clearAllBtn.addEventListener('click', async () => { if (confirm("ARE YOU SURE you want to delete ALL saved timetables? This action is permanent.")) { try { const response = await fetch('/api/clear_all_schedules', { method: 'POST' }); const result = await response.json(); if (!response.ok) throw new Error(result.error); fetchAndDisplaySavedSchedules(); } catch(error) { alert(`Error clearing schedules: ${error.message}`); } } });
    savedSchedulesContentDiv.addEventListener('click', async (event) => { if (event.target.classList.contains('delete-schedule-btn')) { const sectionName = event.target.dataset.section; if (confirm(`Are you sure you want to delete the schedule for "${sectionName}"? This action is permanent.`)) { try { const response = await fetch('/api/delete_schedule', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sectionName }) }); const result = await response.json(); if (!response.ok) throw new Error(result.error); fetchAndDisplaySavedSchedules(); } catch(error) { alert(`Error deleting schedule: ${error.message}`); } } } else if (event.target.closest('.saved-section-header')) { const details = event.target.closest('.saved-section').querySelector('.saved-timetable-details'); if (details) { details.style.display = details.style.display === 'block' ? 'none' : 'block'; } } });
});
