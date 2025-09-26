# Student Complaint Ticketing and Resolution System

This is a Django-based web application for managing, tracking and resolving student complaints across multiple university departments (IT, Maintenance, Rector, Warden, Panel/Data Analyst, Admin).

This README describes how to get the project running locally, how to connect it to a MySQL database, and lists the main application URLs (route paths and Django names).

## Quick overview

- Backend: Django 5.x
- App code: `backend/myapp/` (models, views, templates)
- Templates: `backend/myapp/templates`
- Static files: `backend/myapp/static`

## Quickstart (development)

1. Clone the repository and change into the backend folder:

   ```bash
   git clone https://github.com/BSimow/Student-Complaint-Ticketing-and-Resolution-System.git
   cd "Student-Complaint-Ticketing-and-Resolution-System/backend"
   ```

2. Create and activate a virtual environment (recommended):

   ```bash
   # on Windows (bash shell)
   python -m venv .venv
   source .venv/Scripts/activate

   # on macOS / Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Notes about MySQL client libraries on Windows:

   - `mysqlclient` (the default expected DB driver) requires a C compiler and Microsoft Visual C++ Build Tools on Windows. If you run into build errors, either install the Visual C++ Build Tools or use `PyMySQL` as an alternative (see below).

   Alternative using PyMySQL (if you can't install mysqlclient):

   1. Install PyMySQL:

   ```bash
   pip install PyMySQL
   ```

   2. In `backend/backend/settings.py` add near the top (above DATABASES):

   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```

   This lets Django use PyMySQL as the MySQLdb replacement while keeping `ENGINE: 'django.db.backends.mysql'`.

4. Configure your database (see the "MySQL configuration" section below).

5. Apply migrations (this project contains models that Django manages; some tables like `complaints` and `students` are `managed = False` and expected to already exist in the target database):

   ```bash
   python manage.py migrate
   ```

6. Create a superuser (admin):

   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

8. Open the app in your browser:

   - Login page: http://127.0.0.1:8000/login/

   (Note: the project may use email-as-username in forms; use the admin superuser credentials you created to log in first.)

## MySQL configuration and example

The project uses MySQL in `backend/backend/settings.py` by default. The file already contains a sample `DATABASES` configuration (adjust credentials, host and port to your environment). Example:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'university_complaints',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
```

Important notes about the `students` and `complaints` tables

- This project defines `Student` and `Complaint` models with `managed = False` (they map to existing tables in your MySQL database). That means Django will not create or alter these tables with migrations — you must ensure they exist and match the fields the code expects.

E

Make sure the `students.email` values match the Django `User.email` for proper mapping (the code uses Student.objects.get(email=request.user.email) to find a student's external record).

If your MySQL server uses a different port (the sample settings in the repo use 3307 in one example), update the `PORT` value accordingly.

## All main application routes (paths and Django names)

Top-level: the project routes are defined in `backend/backend/urls.py` and include `myapp.urls`.

List of paths (path -> view name):

- `/admin/` -> Django admin site

- Authentication & student pages

  - `/signup/` -> name: `signup`
  - `/login/` -> name: `login`
  - `/logout/` -> name: `logout`
  - `/student/dashboard/` -> name: `student_dashboard`
  - `/student/profile-settings/` -> name: `student_profile_settings`
  - `/student/new-query/` -> name: `student_new_query` (submit a complaint)
  - `/student/my-queries/` -> name: `student_my_queries` (list your complaints)

- Panel (Finance/Admin) dashboard

  - `/dashboard/panel/` -> name: `panel_dashboard`
  - `/dashboard/panel/members/` -> name: `panel_members`
  - `/dashboard/panel/queries/` -> name: `panel_queries`

- Admin dashboard

  - `/dashboard/admin/` -> name: `dashboard_admin`
  - `/dashboard/admin/members/` -> name: `dashboard_admin_members`
  - `/dashboard/admin/queries/` -> name: `dashboard_admin_queries`

- Warden dashboard

  - `/dashboard/warden/` -> name: `dashboard_warden`
  - `/dashboard/warden/members/` -> name: `dashboard_warden_members`
  - `/dashboard/warden/queries/` -> name: `dashboard_warden_queries`

- Rector dashboard

  - `/dashboard/rector/` -> name: `dashboard_rector`
  - `/dashboard/rector/members/` -> name: `dashboard_rector_members`
  - `/dashboard/rector/queries/` -> name: `dashboard_rector_queries`

- Maintenance dashboard

  - `/dashboard/maintenance/` -> name: `dashboard_maintenance`
  - `/dashboard/maintenance/members/` -> name: `dashboard_maintenance_members`
  - `/dashboard/maintenance/queries/` -> name: `dashboard_maintenance_queries`

- IT dashboard
  - `/dashboard/it/` -> name: `dashboard_it`
  - `/dashboard/it/members/` -> name: `dashboard_it_members`
  - `/dashboard/it/queries/` -> name: `dashboard_it_queries`

These routes are declared in `backend/myapp/urls.py`.

## How the mapping works (Django user -> external students table)

- The app maps a logged-in Django `User` to the external `students` table by email. The `Student` model is `managed = False` and fields include `student_id`, `name`, `email`, `phone`.
- When a student submits a complaint, the code will do a lookup Student.objects.get(email=request.user.email) and use `student_info.student_id` as the `student_id` in the `complaints` insert. Ensure every student user has a matching `students.email` record.

## Debugging and common issues

- "ImportError: mysqlclient not found / wheel build failed":

  - On Windows you often need to install Microsoft Visual C++ Build Tools. Alternatively use the PyMySQL approach described above.

- "Student record not found" message when submitting complaints:

  - Make sure the `students` table contains an entry whose `email` matches the Django user's email.

- Virtual environment issues / unable to import django:
  - Activate the virtualenv before running management commands: `source .venv/Scripts/activate` (Windows bash) or `source .venv/bin/activate` (macOS/Linux).

## Useful commands

```bash
# Run system checks
python manage.py check

# Run migrations (for managed models)
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Open Django DB shell (uses your DATABASES settings)
python manage.py dbshell

# Run the dev server
python manage.py runserver
```

## Contributing

Contributions are welcome. If you plan to change the database mapping (for example, to migrate `students` into Django-managed models), please open an issue to coordinate migrations and data migration steps.

## Contact

If something here is unclear, or you want me to wire up environment-based DB config (using a `.env` + django-environ) or remove the legacy `UserProfile.student_db_id` field, tell me and I can implement that next.
