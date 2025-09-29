from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.db import connection
from django.shortcuts import redirect, render
from django.utils import timezone
from .models import Complaint, Student
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from rest_framework import viewsets
from .models import Complaint
from .serializers import ComplaintSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Complaint

# Profile settings views for each department
def panel_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='panel').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/panel/panel-profile-settings.html')

def admin_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/admin/admin-profile-settings.html')

def warden_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='warden').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/warden/warden-profile-settings.html')

def rector_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='rector').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/rector/rector-profile-settings.html')

def maintenance_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='maintenance').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/maintenance/maintenance-profile-settings.html')

def it_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='it').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/it/it-profile-settings.html')

# Panel (Data Analyst) Dashboards
def dashboard_panel(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='panel').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='Finance_Admin').order_by('-created_at')
    pending_queries = complaints.filter(status='Open').count()
    in_progress_queries = complaints.filter(status='In Progress').count()
    resolved_queries = complaints.filter(status='Resolved').count()
    return render(request, 'dashboards/panel/panel-dashboard.html', {'complaints': complaints, 'pending_queries': pending_queries, 'in_progress_queries': in_progress_queries, 'resolved_queries': resolved_queries})

def dashboard_panel_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='panel').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/panel/panel-members.html')

def dashboard_panel_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='panel').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
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

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all().order_by('-created_at')
    serializer_class = ComplaintSerializer

def dashboard_view(request):
    return render(request, "dashboard.html")

def run_ai(request):
    from myapp.ai.complaint_agent import for_frontend, AIConfigError  # lazy import
    q = request.GET.get("q", "")
    try:
        data = for_frontend(q)
        return JsonResponse(data)
    except AIConfigError as e:
        return JsonResponse({"error": str(e)}, status=500)

# Helper function to redirect user to the correct dashboard based on group

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

    # Fetch student info from MySQL students table using email
    student_info = None
    complaints = []
    try:
        student_info = Student.objects.get(email=request.user.email)
        complaints = Complaint.objects.filter(student_id=student_info.student_id).order_by('-created_at')
    except Student.DoesNotExist:
        student_info = None

    return render(request, 'student/student-dashboard.html', {
        'student_info': student_info,
        'complaints': complaints
    })

def student_profile_settings(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'student/profile-settings.html')

def student_new_query(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        priority = request.POST.get('priority', 'Medium')
        
        # Lookup student in external students table by email
        try:
            student_info = Student.objects.get(email=request.user.email)
            student_db_id = student_info.student_id
        except Student.DoesNotExist:
            messages.error(request, 'Student record not found in external students table. Cannot submit complaint.')
            return redirect('student_new_query')

        # Since the complaints table is managed=False, insert using raw SQL with the matched student_id
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO complaints (student_id, title, description, category, priority, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [student_db_id, title, description, category, priority, 'Open', timezone.now()])

        messages.success(request, 'Complaint submitted successfully!')
        return redirect('student_my_queries')
    return render(request, 'student/new-query.html')

def student_my_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # Lookup student in external students table by email
    try:
        student_info = Student.objects.get(email=request.user.email)
        student_db_id = student_info.student_id
    except Student.DoesNotExist:
        # If student record is not found, show empty list and a message
        messages.info(request, 'No student record found for your account.')
        complaints = []
        return render(request, 'student/my-queries.html', {'complaints': complaints})

    complaints = Complaint.objects.filter(student_id=student_db_id).order_by('-created_at')
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
    if not (request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    # Admin can see all complaints for oversight
    complaints = Complaint.objects.filter(category='Certificates_Documents').order_by('-created_at')
    return render(request, 'dashboards/admin/admin-dashboard.html', {'complaints': complaints})

def dashboard_admin_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/admin/admin-members.html')

def dashboard_admin_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    # Admin can see all complaints for oversight
    complaints = Complaint.objects.filter(category='Certificates_Documents').order_by('-created_at')
    return render(request, 'dashboards/admin/admin-queries.html', {'complaints': complaints})

def dashboard_warden(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='warden').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='Certificates_Documents').order_by('-created_at')
    pending_queries = complaints.filter(status='Open').count()
    in_progress_queries = complaints.filter(status='In Progress').count()
    resolved_queries = complaints.filter(status='Resolved').count()
    return render(request, 'dashboards/warden/warden-dashboard.html', {'complaints': complaints, 'pending_queries': pending_queries, 'in_progress_queries': in_progress_queries, 'resolved_queries': resolved_queries})

def dashboard_warden_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='warden').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/warden/warden-members.html')

def dashboard_warden_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='warden').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='Certificates_Documents').order_by('-created_at')
    return render(request, 'dashboards/warden/warden-queries.html', {'complaints': complaints})

def dashboard_rector(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='rector').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='Courses_Training').order_by('-created_at')
    pending_queries = complaints.filter(status='Open').count()
    in_progress_queries = complaints.filter(status='In Progress').count()
    resolved_queries = complaints.filter(status='Resolved').count()
    return render(request, 'dashboards/rector/rector-dashboard.html', {'complaints': complaints, 'pending_queries': pending_queries, 'in_progress_queries': in_progress_queries, 'resolved_queries': resolved_queries})

def dashboard_rector_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='rector').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/rector/rector-members.html')

def dashboard_rector_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='rector').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='Courses_Training').order_by('-created_at')
    return render(request, 'dashboards/rector/rector-queries.html', {'complaints': complaints})

def dashboard_maintenance(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='maintenance').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='Facilities_Logistics').order_by('-created_at')
    pending_queries = complaints.filter(status='Open').count()
    in_progress_queries = complaints.filter(status='In Progress').count()
    resolved_queries = complaints.filter(status='Resolved').count()
    return render(request, 'dashboards/maintenance/maintenance-dashboard.html', {'complaints': complaints, 'pending_queries': pending_queries, 'in_progress_queries': in_progress_queries, 'resolved_queries': resolved_queries})

def dashboard_maintenance_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='maintenance').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/maintenance/maintenance-members.html')

def dashboard_maintenance_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='maintenance').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='Facilities_Logistics').order_by('-created_at')
    return render(request, 'dashboards/maintenance/maintenance-queries.html', {'complaints': complaints})

def dashboard_it(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='it').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='IT_Support').order_by('-created_at')
    pending_queries = complaints.filter(status='Open').count()
    in_progress_queries = complaints.filter(status='In Progress').count()
    resolved_queries = complaints.filter(status='Resolved').count()
    return render(request, 'dashboards/it/it-dashboard.html', {'complaints': complaints, 'pending_queries': pending_queries, 'in_progress_queries': in_progress_queries, 'resolved_queries': resolved_queries})

def dashboard_it_members(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='it').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    return render(request, 'dashboards/it/it-members.html')

def dashboard_it_queries(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not (request.user.groups.filter(name='it').exists() or request.user.groups.filter(name='admin').exists() or request.user.is_superuser):
        return redirect('login')
    complaints = Complaint.objects.filter(category='IT_Support').order_by('-created_at')
    return render(request, 'dashboards/it/it-queries.html', {'complaints': complaints})

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all().order_by('-created_at')
    serializer_class = ComplaintSerializer


@require_POST
def ai_analyze(request):
    # Accept JSON { "text": "..." } or form-encoded "text=..."
    ct = request.META.get("CONTENT_TYPE", "")
    if ct.startswith("application/json"):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("invalid JSON")
        text = (payload.get("text") or "").strip()
    else:
        text = (request.POST.get("text") or "").strip()

    if not text:
        return HttpResponseBadRequest("text required")

    # call the agent directly (no HTTP between services)
    result = ai_agent(text, model="gpt-4o-mini", temperature=0.0, max_tokens=1200)

    if isinstance(result, dict) and "error" in result:
        return JsonResponse({"error": result["error"]}, status=502)

    ui = for_frontend(result)
    return JsonResponse({"ui": ui, "raw": result})

@api_view(['GET'])
def kpis(request):
    total = Complaint.objects.count()
    by_status = Complaint.objects.values('status').annotate(c=Count('id')).order_by()
    # optional: by_department if you have that field
    try:
        by_department = Complaint.objects.values('department').annotate(c=Count('id')).order_by()
    except Exception:
        by_department = []
    ts = (Complaint.objects
          .annotate(d=TruncDate('created_at'))
          .values('d').annotate(c=Count('id')).order_by('d'))
    return Response({
        "total": total,
        "by_status": list(by_status),
        "by_department": list(by_department),  # falls back to []
        "timeseries": list(ts),
    })
