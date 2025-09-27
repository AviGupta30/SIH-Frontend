document.addEventListener('DOMContentLoaded', () => {

    // --- GLOBAL ELEMENT SELECTORS ---
    const body = document.body;
    const loginContainer = document.getElementById('login-container');
    const dashboardContainer = document.getElementById('dashboard-container');
    
    // --- LOGIN LOGIC ---
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');

    const showDashboard = () => {
        loginContainer.classList.add('hidden');
        dashboardContainer.classList.remove('hidden');
        // IMPORTANT: Initialize all dashboard features AFTER showing it.
        initializeDashboard();
    };

    const showLogin = () => {
        loginContainer.classList.remove('hidden');
        dashboardContainer.classList.add('hidden');
    };

    const checkLoginStatus = () => {
        if (localStorage.getItem('isLoggedIn') === 'true') {
            showDashboard();
        } else {
            showLogin();
        }
    };

    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            const usernameInput = document.getElementById('username');
            const passwordInput = document.getElementById('password');
            const rememberMeCheckbox = document.getElementById('remember-me');
            const errorMessage = document.getElementById('error-message');
            if (usernameInput.value === 'avigupta30' && passwordInput.value === '12345678') {
                if (rememberMeCheckbox.checked) {
                    localStorage.setItem('isLoggedIn', 'true');
                }
                showDashboard();
                errorMessage.classList.add('hidden');
            } else {
                errorMessage.classList.remove('hidden');
                passwordInput.value = '';
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('isLoggedIn');
            window.location.reload();
        });
    }

    // --- This function now contains ALL dashboard-related code ---
    function initializeDashboard() {
        const themeToggle = document.getElementById('theme-toggle');
        const mainHeaderTitle = document.getElementById('main-header-title');
        const backToMainBtn = document.getElementById('back-to-main');
        const allViews = dashboardContainer.querySelectorAll('.view-container');
        let lastActiveViewId = 'dashboard-section';

        // --- THEME SWITCHER LOGIC ---
        const applySavedTheme = () => {
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'light') {
                body.classList.add('light-theme');
                if (themeToggle) themeToggle.checked = true;
            } else {
                body.classList.remove('light-theme');
                if (themeToggle) themeToggle.checked = false;
            }
        };
        if (themeToggle) {
            themeToggle.addEventListener('change', () => {
                body.classList.toggle('light-theme');
                localStorage.setItem('theme', themeToggle.checked ? 'light' : 'dark');
            });
        }
        applySavedTheme();

        // --- LIVE WEATHER API LOGIC ---
        const fetchWeatherData = () => {
            const apiKey = 'fd44e6631598b259cae16043e5241009';
            const lat = 28.7041;
            const lon = 77.1025; // Delhi
            const apiUrl = `https://api.openweathermap.org/data/2.5/forecast?lat=${lat}&lon=${lon}&appid=${apiKey}&units=metric`;

            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Weather data not available. Check API key.');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.list) {
                        updateWeatherUI('today', data.list[0]);
                        updateWeatherUI('tomorrow', data.list[8]); // 24 hours later
                    }
                })
                .catch(error => {
                    console.error('Error fetching weather:', error);
                    document.getElementById('today-weather-desc').textContent = 'Could not load weather';
                    document.getElementById('tomorrow-weather-desc').textContent = 'Could not load weather';
                });
        };

        const updateWeatherUI = (day, weatherData) => {
            const mainCondition = weatherData.weather[0].main;
            const description = weatherData.weather[0].description;
            const temp = Math.round(weatherData.main.temp);
            let icon = '...';
            let campusStatus = `Campus is operational.`;
            let onlineProb = '5-15%';

            switch (mainCondition) {
                case 'Thunderstorm': icon = '⛈️'; campusStatus = 'Campus closed. Classes are ONLINE.'; onlineProb = '100%'; break;
                case 'Drizzle': icon = '🌦️'; campusStatus = 'Campus open. Carry an umbrella!'; onlineProb = '40-60%'; break;
                case 'Rain': icon = '🌧️'; campusStatus = 'Heavy rain expected. Online classes likely.'; onlineProb = '70-90%'; break;
                case 'Snow': icon = '❄️'; campusStatus = 'Campus closed due to snow.'; onlineProb = '100%'; break;
                case 'Clear': icon = '☀️'; onlineProb = '0-5%'; break;
                case 'Clouds': icon = '☁️'; break;
                default: icon = '🌫️'; campusStatus = 'Reduced visibility on campus.'; onlineProb = '20-40%'; break;
            }

            document.getElementById(`${day}-weather-icon`).textContent = icon;
            document.getElementById(`${day}-weather-desc`).innerHTML = `${temp}°C, ${description.replace(/\b\w/g, l => l.toUpperCase())}`;
            document.getElementById(`${day}-campus-status`).textContent = campusStatus;
            document.getElementById(`${day}-online-prob`).textContent = `Online Class Probability: ${onlineProb}`;
        };
        fetchWeatherData();
        
        // --- VIEW SWITCHING LOGIC ---
        const sidebarLinks = document.querySelectorAll('.sidebar nav a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.dataset.target;
                if (!targetId) return;

                sidebarLinks.forEach(l => l.parentElement.classList.remove('active'));
                link.parentElement.classList.add('active');
                
                showMainSection(targetId);
            });
        });

        const showMainSection = (targetId) => {
            lastActiveViewId = targetId;
            allViews.forEach(section => {
                section.classList.toggle('hidden', section.id !== targetId);
                section.classList.toggle('active', section.id === targetId);
            });
            backToMainBtn.classList.add('hidden');
            mainHeaderTitle.classList.remove('hidden');
        };

        // --- CLASSROOM & DETAIL VIEW LOGIC ---
        document.querySelector('.classroom-grid').addEventListener('click', (e) => {
            const cardLink = e.target.closest('.classroom-card');
            if (!cardLink) return;
            
            allViews.forEach(section => section.classList.add('hidden'));
            const classDetailView = document.getElementById('class-detail-view');
            classDetailView.classList.remove('hidden');
            classDetailView.classList.add('active');

            backToMainBtn.classList.remove('hidden');
            mainHeaderTitle.classList.add('hidden');
            
            const { classname, classcode, bg, prof, profImg } = cardLink.dataset;
            document.getElementById('class-detail-title').textContent = classname;
            document.getElementById('class-detail-code').textContent = classcode;
            document.querySelector('.class-detail-header').className = `class-detail-header ${bg}`;
            // (You would add logic here to populate stream/classwork if it were dynamic)
        });

        backToMainBtn.addEventListener('click', () => {
            showMainSection(lastActiveViewId);
        });

        const detailTabsContainer = document.querySelector('.class-detail-tabs');
        detailTabsContainer.addEventListener('click', (e) => {
            const clickedTab = e.target.closest('.tab-btn');
            if (!clickedTab) return;
            const targetPaneId = clickedTab.dataset.target;
            detailTabsContainer.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            clickedTab.classList.add('active');
            document.querySelectorAll('.tab-content-pane').forEach(pane => {
                pane.classList.toggle('hidden', pane.id !== targetPaneId);
            });
        });
        
        // --- ADDED: Logic for weather tabs ("Today" / "Tomorrow") ---
        const advisoryTabs = document.querySelectorAll('.system-advisory .tabs button');
        advisoryTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const container = tab.closest('.system-advisory');
                const targetContent = tab.dataset.tab;
                
                container.querySelectorAll('.tabs button').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                container.querySelectorAll('.tab-content .content').forEach(content => {
                    content.classList.toggle('active', content.id === targetContent);
                });
            });
        });

        // --- DYNAMIC ATTENDANCE CALCULATION ---
        document.querySelectorAll('.attendance-card').forEach(card => {
            const attended = parseFloat(card.dataset.attended);
            const total = parseFloat(card.dataset.total);
            const percentage = total > 0 ? (attended / total) * 100 : 0;
            const progressBarFill = card.querySelector('.progress-bar-fill');
            const percentageText = card.querySelector('.percentage');
            if (progressBarFill) {
                progressBarFill.style.width = `${percentage}%`;
            }
            if (percentageText) {
                percentageText.textContent = `${percentage.toFixed(1)}%`;
            }
            
            const statusText = card.querySelector('.status-text');
            if(statusText && progressBarFill) {
                let statusClass = 'danger';
                if (percentage >= 75) statusClass = 'safe';
                else if (percentage >= 60) statusClass = 'warning';
                statusText.textContent = statusClass.charAt(0).toUpperCase() + statusClass.slice(1);
                statusText.className = `status-text ${statusClass}`;
                progressBarFill.className = `progress-bar-fill ${statusClass}`;
            }
        });
    }

    // --- INITIAL PAGE LOAD ---
    checkLoginStatus();
});