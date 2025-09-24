
from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
	student_id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=255, blank=True, null=True)
	email = models.CharField(max_length=255, blank=True, null=True)
	phone = models.CharField(max_length=255, blank=True, null=True)

	class Meta:
		db_table = 'students'
		managed = False

	def __str__(self):
		return f"{self.name} (ID: {self.student_id})"



class UserProfile(models.Model):
	USER_ROLES = [
		('student', 'Student'),
		('admin', 'Admin'),
		('warden', 'Warden'),
		('rector', 'Rector'),
		('maintenance', 'Maintenance'),
		('it', 'IT'),
		('panel', 'Panel'),
	]
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
	student_db_id = models.IntegerField(null=True, blank=True)  # Maps to student ID in external DB

	def __str__(self):
		return f"{self.user.email} - {self.role}"

class Complaint(models.Model):
	STATUS_CHOICES = [
		('Open', 'Open'),
		('In Progress', 'In Progress'),
		('Resolved', 'Resolved'),
		('Closed', 'Closed'),
	]

	DEPARTMENT_CHOICES = [
		('it', 'IT'),
		('maintenance', 'Maintenance'),
		('admin', 'Admin'),
		('rector', 'Rector'),
		('warden', 'Warden'),
		('panel', 'Panel'),
	]

	CATEGORY_CHOICES = [
		('Certificates_Documents', 'Certificates & Documents'),
		('Finance_Admin', 'Finance & Admin'),
		('IT_Support', 'IT Support'),
		('Courses_Training', 'Courses & Training'),
		('Facilities_Logistics', 'Facilities & Logistics'),
	]

	PRIORITY_CHOICES = [
		('Low', 'Low'),
		('Medium', 'Medium'),
		('High', 'High'),
		('Critical', 'Critical'),
	]

	complaint_id = models.AutoField(primary_key=True)
	student_id = models.IntegerField()  # Reference to student, not FK to User
	title = models.CharField(max_length=255)
	description = models.TextField()
	category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
	priority = models.CharField(max_length=32, choices=PRIORITY_CHOICES, default='Medium')
	status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='Open')
	created_at = models.DateTimeField()
	resolved_at = models.DateTimeField(null=True, blank=True)

	# Add a virtual property to map to departments based on category
	@property
	def department(self):
		category_to_dept = {
			'IT_Support': 'it',
			'Facilities_Logistics': 'maintenance',
			'Finance_Admin': 'admin',
			'Courses_Training': 'rector',
			'Certificates_Documents': 'warden',
		}
		return category_to_dept.get(self.category, 'admin')

	class Meta:
		db_table = 'complaints'
		managed = False  # Don't let Django manage this table

	def __str__(self):
		return f"{self.title} (Student ID: {self.student_id}) - {self.category}"

# Keep Query model for backward compatibility if needed
class Query(models.Model):
	STATUS_CHOICES = [
		('Pending', 'Pending'),
		('In Progress', 'In Progress'),
		('Resolved', 'Resolved'),
		('Closed', 'Closed'),
	]
	CATEGORY_CHOICES = [
		('academic', 'Academic'),
		('financial', 'Financial'),
		('technical', 'Technical'),
		('administrative', 'Administrative'),
		('other', 'Other'),
	]
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	subject = models.CharField(max_length=255)
	description = models.TextField()
	category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
	status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='Pending')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.subject} ({self.user.email})"
