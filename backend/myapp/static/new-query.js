// new-query.js

document.addEventListener('DOMContentLoaded', function() {
    // User menu toggle
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userMenu = document.getElementById('userMenu');
    
    if (userMenuBtn && userMenu) {
        userMenuBtn.addEventListener('click', function() {
            userMenu.classList.toggle('hidden');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (userMenuBtn && userMenu && !userMenuBtn.contains(e.target) && !userMenu.contains(e.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }

    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-open');
        });
    }

    // Form submission
    const queryForm = document.getElementById('queryForm');
    if (queryForm) {
        queryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Check if terms checkbox is checked
            const termsCheckbox = document.getElementById('terms');
            if (!termsCheckbox.checked) {
                alert('Please acknowledge the terms before submitting.');
                return;
            }
            // Basic validation
            const category = document.getElementById('category').value;
            const subject = document.getElementById('subject').value;
            const description = document.getElementById('description').value;
            if (!category || !subject || !description) {
                alert('Please fill out all required fields.');
                return;
            }
            // In a real app, this would submit the form data to the server
            alert('Your query has been submitted successfully! Reference: Q-' + Math.floor(1000 + Math.random() * 9000));
            // Redirect to dashboard
            window.location.href = 'student-dashboard.html';
        });
    }

    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // In a real app, this would clear the session/token
            window.location.href = 'index.html';
        });
    }
});
