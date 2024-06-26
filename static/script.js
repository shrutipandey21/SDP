document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('pay-button').addEventListener('click', function() {
        alert('Payment feature is not implemented yet.');
    });

    document.getElementById('contact-us').addEventListener('click', function() {
        alert('Contacting customer service...');
    });

    document.getElementById('update-profile').addEventListener('click', function() {
        let fullName = document.getElementById('full-name').value;
        if (fullName) {
            alert(`Profile updated: ${fullName}`);
        } else {
            alert('Please enter your full name.');
        }
    });

    document.querySelectorAll('.check-balance').forEach(function(element) {
        element.addEventListener('click', function() {
            alert('Checking balance feature is not implemented yet.');
        });
    });

    // Toggle Sidebar for Mobile
    const hamburger = document.getElementById('hamburger');
    const sidebar = document.querySelector('.sidebar');

    hamburger.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });

    // Toggle Dark Mode
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;

    themeToggle.addEventListener('click', function() {
        body.classList.toggle('dark-mode');
        if (body.classList.contains('dark-mode')) {
            themeToggle.textContent = 'Switch to Light Mode';
        } else {
            themeToggle.textContent = 'Switch to Dark Mode';
        }
    });
});
