from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# Profile settings views for each department
def panel_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='panel').exists():
        return redirect('login')
    return render(request, 'dashboards/panel/panel-profile-settings.html')

def admin_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='admin').exists():
        return redirect('login')
    return render(request, 'dashboards/admin/admin-profile-settings.html')

def warden_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='warden').exists():
        return redirect('login')
    return render(request, 'dashboards/warden/warden-profile-settings.html')

def rector_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='rector').exists():
        return redirect('login')
    return render(request, 'dashboards/rector/rector-profile-settings.html')

def maintenance_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='maintenance').exists():
        return redirect('login')
    return render(request, 'dashboards/maintenance/maintenance-profile-settings.html')

def it_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='it').exists():
        return redirect('login')
    return render(request, 'dashboards/it/it-profile-settings.html')

# Panel (Data Analyst) Dashboards
def dashboard_panel(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='panel').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='Finance_Admin').order_by('-created_at')
    return render(request, 'dashboards/panel/panel-dashboard.html', {'complaints': complaints})

def dashboard_panel_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='panel').exists():
        return redirect('login')
    return render(request, 'dashboards/panel/panel-members.html')

def dashboard_panel_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='panel').exists():
        return redirect('login')
    from .models import Complaint
    # Panel handles Finance & Admin category
    complaints = Complaint.objects.filter(category='Finance_Admin').order_by('-created_at')
    return render(request, 'dashboards/panel/panel-queries.html', {'complaints': complaints})


def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect_user_dashboard(request.user)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect_user_dashboard(user)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

# Helper function to redirect user to the correct dashboard based on group
from django.shortcuts import redirect
from django.contrib.auth.models import Group
def redirect_user_dashboard(user):
    if user.groups.filter(name='it').exists():
        return redirect('dashboard_it')
    elif user.groups.filter(name='rector').exists():
        return redirect('dashboard_rector')
    elif user.groups.filter(name='maintenance').exists():
        return redirect('dashboard_maintenance')
    elif user.groups.filter(name='warden').exists():
        return redirect('dashboard_warden')
    elif user.groups.filter(name='panel').exists():
        return redirect('panel_dashboard')
    else:
        return redirect('student_dashboard')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    if request.method == 'POST':
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'signup.html')
        username = email  # Use email as username
        user = User.objects.create_user(username=username, email=email, password=password, first_name=full_name)
        login(request, user)
        return redirect('student_dashboard')
    return render(request, 'signup.html')

def student_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'student/student-dashboard.html')

def student_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'student/profile-settings.html')

def student_new_query(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        from .models import Complaint
        from django.utils import timezone
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        priority = request.POST.get('priority', 'Medium')
        
        # Since the table is managed=False, we need to insert manually
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO complaints (student_id, title, description, category, priority, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [request.user.id, title, description, category, priority, 'Open', timezone.now()])
        
        messages.success(request, 'Complaint submitted successfully!')
        return redirect('student_my_queries')
    return render(request, 'student/new-query.html')

def student_my_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    from .models import Complaint
    # Assuming we can match student_id to user.id or use another mapping
    complaints = Complaint.objects.filter(student_id=request.user.id).order_by('-created_at')
    return render(request, 'student/my-queries.html', {'complaints': complaints})

def admin_index(request):
    return redirect('/admin/')

def admin_users_management(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'panel/panel_usersmanagement.html')

def admin_tickets(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'panel/panel_tickets.html')

def admin_departments(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'panel/panel_departments.html')

def dashboard_admin(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='admin').exists():
        return redirect('login')
    from .models import Complaint
    # Admin can see all complaints for oversight
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'dashboards/admin/admin-dashboard.html', {'complaints': complaints})

def dashboard_admin_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='admin').exists():
        return redirect('login')
    return render(request, 'dashboards/admin/admin-members.html')

def dashboard_admin_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='admin').exists():
        return redirect('login')
    from .models import Complaint
    # Admin can see all complaints for oversight
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'dashboards/admin/admin-queries.html', {'complaints': complaints})

def dashboard_warden(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='warden').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='Certificates_Documents').order_by('-created_at')
    return render(request, 'dashboards/warden/warden-dashboard.html', {'complaints': complaints})

def dashboard_warden_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='warden').exists():
        return redirect('login')
    return render(request, 'dashboards/warden/warden-members.html')

def dashboard_warden_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='warden').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='Certificates_Documents').order_by('-created_at')
    return render(request, 'dashboards/warden/warden-queries.html', {'complaints': complaints})

def dashboard_rector(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='rector').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='Courses_Training').order_by('-created_at')
    return render(request, 'dashboards/rector/rector-dashboard.html', {'complaints': complaints})

def dashboard_rector_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='rector').exists():
        return redirect('login')
    return render(request, 'dashboards/rector/rector-members.html')

def dashboard_rector_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='rector').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='Courses_Training').order_by('-created_at')
    return render(request, 'dashboards/rector/rector-queries.html', {'complaints': complaints})

def dashboard_maintenance(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='maintenance').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='Facilities_Logistics').order_by('-created_at')
    return render(request, 'dashboards/maintenance/maintenance-dashboard.html', {'complaints': complaints})

def dashboard_maintenance_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='maintenance').exists():
        return redirect('login')
    return render(request, 'dashboards/maintenance/maintenance-members.html')

def dashboard_maintenance_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='maintenance').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='Facilities_Logistics').order_by('-created_at')
    return render(request, 'dashboards/maintenance/maintenance-queries.html', {'complaints': complaints})

def dashboard_it(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='it').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='IT_Support').order_by('-created_at')
    return render(request, 'dashboards/it/it-dashboard.html', {'complaints': complaints})

def dashboard_it_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='it').exists():
        return redirect('login')
    return render(request, 'dashboards/it/it-members.html')

def dashboard_it_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.groups.filter(name='it').exists():
        return redirect('login')
    from .models import Complaint
    complaints = Complaint.objects.filter(category='IT_Support').order_by('-created_at')
    return render(request, 'dashboards/it/it-queries.html', {'complaints': complaints})