# Student Complaint Ticketing and Resolution System

A Django-based web application for managing, tracking, and resolving student complaints across multiple university departments (IT, Maintenance, Rector, Warden, Panel/Data Analyst, Admin).

## Features
- User authentication (students, staff, department heads, analysts, admins)
- Role-based dashboards and navigation
- Submit, track, and manage complaints/tickets
- Department-specific dashboards and analytics
- Profile management and password change for all roles
- Group-based access control (users cannot access other department dashboards)
- Responsive UI with Tailwind CSS and Chart.js for analytics

## Project Structure
```
Non-Acedamic-Issue-Tracker/
├── backend/
│   ├── manage.py
│   ├── backend/
│   ├── core/
│   │   ├── static/
│   │   └── templates/
│   │       ├── login.html, signup.html, ...
│   │       └── dashboards/
│   │           ├── admin/
│   │           ├── it/
│   │           ├── maintenance/
│   │           ├── panel/
│   │           ├── rector/
│   │           └── warden/
│   └── myapp/
│       ├── models.py, views.py, urls.py, ...
└── README.md
```

## Getting Started
1. **Clone the repository:**
   ```sh
   git clone https://github.com/BSimow/Student-Complaint-Ticketing-and-Resolution-System.git
   cd Student-Complaint-Ticketing-and-Resolution-System/backend
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
4. **Create a superuser (admin):**
   ```sh
   python manage.py createsuperuser
   ```
5. **Run the development server:**
   ```sh
   python manage.py runserver
   ```
6. **Access the app:**
   - Visit `http://127.0.0.1:8000/Login` in your browser.

## Usage
- Students can submit and track complaints.
- Department staff can view and manage tickets relevant to their group.
- Admins and analysts have access to advanced dashboards and analytics.
- Each user role has a dedicated dashboard and profile settings page.

## Technologies Used
- Python, Django
- SQLite (default, can be changed)
- Tailwind CSS, Chart.js, ECharts
- HTML5, JavaScript

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.
