document.addEventListener('DOMContentLoaded', () => {
    
    // --- THEME SWITCHER LOGIC ---
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    // Function to apply the saved theme on page load
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

    // Event listener for the toggle switch
    if (themeToggle) {
        themeToggle.addEventListener('change', () => {
            if (themeToggle.checked) {
                body.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
            } else {
                body.classList.remove('light-theme');
                localStorage.setItem('theme', 'dark');
            }
        });
    }
    
    // --- INITIALIZE PAGE ---
    applySavedTheme();
    console.log('SmartFlex homepage loaded successfully.');
});