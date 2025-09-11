// Dashboard functionality

// Initialize charts when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    initEventListeners();
    initQueryManagement();
    initDashboardSpecifics();
    initSidebar();
});

// Initialize sidebar functionality
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    // Set initial state
    if (window.innerWidth < 768) {
        sidebar.classList.add('-translate-x-full');
        mainContent.classList.remove('ml-64');
    } else {
        sidebar.classList.remove('-translate-x-full');
        mainContent.classList.add('ml-64');
    }

    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth < 768) {
            sidebar.classList.add('-translate-x-full');
            mainContent.classList.remove('ml-64');
        } else {
            sidebar.classList.remove('-translate-x-full');
            mainContent.classList.add('ml-64');
        }
    });

    // Handle sidebar toggle
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full');
            mainContent.classList.toggle('ml-64');
        });
    }

    // Handle active navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath.split('/').pop()) {
            link.classList.remove('text-gray-600', 'hover:bg-gray-50');
            link.classList.add('text-primary', 'bg-red-50');
        }
    });
}

// Initialize charts with data
function initCharts() {
    // Fee Collection Chart
    const feeChartCtx = document.getElementById('feeCollectionChart');
    if (feeChartCtx) {
        new Chart(feeChartCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Fee Collection',
                    data: [65000, 59000, 80000, 81000, 56000, 95000],
                    borderColor: '#a52a2a',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(165, 42, 42, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Registration Trends Chart
    const registrationChartCtx = document.getElementById('registrationTrendsChart');
    if (registrationChartCtx) {
        new Chart(registrationChartCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'New Registrations',
                    data: [65, 59, 80, 81, 56, 95],
                    backgroundColor: '#a52a2a',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Ticket Trends Chart
    const ticketTrendsChartCtx = document.getElementById('ticketTrendsChart');
    if (ticketTrendsChartCtx) {
        new Chart(ticketTrendsChartCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'New Tickets',
                    data: [12, 19, 15, 25, 22, 30, 28],
                    borderColor: '#a52a2a',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(165, 42, 42, 0.1)'
                }, {
                    label: 'Resolved Tickets',
                    data: [8, 15, 12, 20, 18, 25, 22],
                    borderColor: '#4CAF50',
                    tension: 0.4,
                    fill: true,
                    backgroundColor: 'rgba(76, 175, 80, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Department Workload Chart
    const departmentWorkloadChartCtx = document.getElementById('departmentWorkloadChart');
    if (departmentWorkloadChartCtx) {
        new Chart(departmentWorkloadChartCtx, {
            type: 'pie',
            data: {
                labels: ['IT', 'Maintenance', 'Admin', 'Security', 'Housekeeping'],
                datasets: [{
                    data: [45, 38, 25, 15, 20],
                    backgroundColor: [
                        '#a52a2a',  // IT - maroon
                        '#4CAF50',  // Maintenance - green
                        '#FF9800',  // Admin - orange
                        '#2196F3',  // Security - blue
                        '#9C27B0'   // Housekeeping - purple
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Department Workload Distribution',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                }
            }
        });
    }

    // Query Categories Chart
    const queryCategoriesChartCtx = document.getElementById('queryCategoriesChart');
    if (queryCategoriesChartCtx) {
        new Chart(queryCategoriesChartCtx, {
            type: 'doughnut',
            data: {
                labels: ['Academic', 'Hostel', 'Financial', 'Technical', 'Other'],
                datasets: [{
                    data: [30, 25, 20, 15, 10],
                    backgroundColor: [
                        '#a52a2a',
                        '#4CAF50',
                        '#FF9800',
                        '#2196F3',
                        '#9C27B0'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Resolution Time Chart
    const resolutionTimeChartCtx = document.getElementById('resolutionTimeChart');
    if (resolutionTimeChartCtx) {
        new Chart(resolutionTimeChartCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                datasets: [{
                    label: 'Average Resolution Time (hours)',
                    data: [2.5, 2.8, 2.2, 2.0, 2.3],
                    backgroundColor: '#a52a2a',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

// Initialize event listeners
function initEventListeners() {
    // User menu toggle
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userMenu = document.getElementById('userMenu');
    
    if (userMenuBtn && userMenu) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userMenu.classList.toggle('hidden');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!userMenuBtn.contains(e.target) && !userMenu.contains(e.target)) {
                userMenu.classList.add('hidden');
            }
        });
    }

    // Add click handlers for action buttons
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const taskItem = this.closest('.task-item');
            const taskId = taskItem.querySelector('.task-id').textContent;
            const taskTitle = taskItem.querySelector('h4').textContent;
            console.log(`Processing task ${taskId}: ${taskTitle}`);
            // In a real app, this would trigger the appropriate action
            alert(`Processing task ${taskId}: ${taskTitle}`);
        });
    });
}

// Initialize query management functionality
function initQueryManagement() {
    const queryModal = document.getElementById('queryModal');
    const viewButtons = document.querySelectorAll('button:contains("View")');
    const acceptButtons = document.querySelectorAll('button:contains("Accept")');
    const updateButtons = document.querySelectorAll('button:contains("Update")');

    // View query details
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const queryId = row.querySelector('td:first-child').textContent;
            const student = row.querySelector('td:nth-child(2)').textContent;
            const subject = row.querySelector('td:nth-child(3)').textContent;
            
            // Populate modal with query details
            document.getElementById('modalQueryId').textContent = queryId;
            document.getElementById('modalStudent').textContent = student;
            document.getElementById('modalSubject').textContent = subject;
            document.getElementById('modalDescription').textContent = 'Detailed description of the query...'; // This would come from your backend
            
            // Show modal
            queryModal.classList.remove('hidden');
        });
    });

    // Accept query
    acceptButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const queryId = row.querySelector('td:first-child').textContent;
            
            // Update status in the table
            const statusCell = row.querySelector('td:nth-child(5)');
            statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">In Progress</span>';
            
            // Update button text
            this.textContent = 'Update';
            this.classList.remove('text-primary', 'hover:text-red-700');
            this.classList.add('text-gray-600', 'hover:text-gray-900');
            
            // Show success notification
            showNotification('Query accepted successfully', 'success');
        });
    });

    // Update query status
    updateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const queryId = row.querySelector('td:first-child').textContent;
            
            // Show update modal
            queryModal.classList.remove('hidden');
        });
    });

    // Close modal when clicking outside
    queryModal.addEventListener('click', function(e) {
        if (e.target === queryModal) {
            queryModal.classList.add('hidden');
        }
    });

    // Handle modal close button
    const modalCloseButton = queryModal.querySelector('button:contains("Cancel")');
    if (modalCloseButton) {
        modalCloseButton.addEventListener('click', () => {
            queryModal.classList.add('hidden');
        });
    }

    // Handle response submission
    const submitButton = queryModal.querySelector('button:contains("Submit Response")');
    if (submitButton) {
        submitButton.addEventListener('click', () => {
            const response = queryModal.querySelector('textarea').value;
            if (response.trim()) {
                // Here you would typically send the response to your backend
                console.log('Submitting response:', response);
                
                // Close modal
                queryModal.classList.add('hidden');
                
                // Show success notification
                showNotification('Response submitted successfully', 'success');
            } else {
                showNotification('Please enter a response', 'error');
            }
        });
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Function to fetch real data (would be implemented in a real app)
async function fetchDashboardData() {
    try {
        // This would be replaced with actual API calls
        const response = await fetch('/api/dashboard/stats');
        if (!response.ok) {
            throw new Error('Failed to fetch dashboard data');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        return null;
    }
}

function initDashboardSpecifics() {
    // Initialize dashboard-specific functionality
    const dashboard = document.body.className.includes('admin') ? 'admin' :
                     document.body.className.includes('it') ? 'it' :
                     document.body.className.includes('maintenance') ? 'maintenance' :
                     document.body.className.includes('rector') ? 'rector' :
                     document.body.className.includes('warden') ? 'warden' : null;

    if (!dashboard) return;

    // Add dashboard-specific event listeners and functionality
    switch(dashboard) {
        case 'admin':
            initAdminDashboard();
            break;
        case 'it':
            initITDashboard();
            break;
        case 'maintenance':
            initMaintenanceDashboard();
            break;
        case 'rector':
            initRectorDashboard();
            break;
        case 'warden':
            initWardenDashboard();
            break;
    }
}

function handleAction(action, id) {
    console.log(`Processing ${action} for item ${id}`);
    showNotification(`${action} action initiated for item ${id}`, 'success');
}

function showQueryDetails(queryId, student, subject) {
    const modal = document.getElementById('queryModal');
    if (!modal) return;

    document.getElementById('modalQueryId').textContent = queryId;
    document.getElementById('modalStudent').textContent = student;
    document.getElementById('modalSubject').textContent = subject;
    document.getElementById('modalDescription').textContent = 'Detailed description of the query...';
    
    modal.classList.remove('hidden');
}

function acceptQuery(queryId, row) {
    const statusCell = row.querySelector('td:nth-child(5)');
    if (statusCell) {
        statusCell.innerHTML = '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">In Progress</span>';
    }

    const button = row.querySelector('button:contains("Accept"), button:contains("Start Work")');
    if (button) {
        button.textContent = 'Update';
        button.classList.remove('text-primary', 'hover:text-red-700');
        button.classList.add('text-gray-600', 'hover:text-gray-900');
    }

    showNotification('Query accepted successfully', 'success');
}

function showUpdateModal(queryId) {
    const modal = document.getElementById('queryModal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function submitResponse(response) {
    const modal = document.getElementById('queryModal');
    if (modal) {
        modal.classList.add('hidden');
    }
    showNotification('Response submitted successfully', 'success');
}

// Dashboard-specific initialization functions
function initAdminDashboard() {
    // Admin-specific functionality
}

function initITDashboard() {
    // IT-specific functionality
}

function initMaintenanceDashboard() {
    // Maintenance-specific functionality
}

function initRectorDashboard() {
    // Rector-specific functionality
}

function initWardenDashboard() {
    // Warden-specific functionality
} 