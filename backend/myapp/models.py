

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	USER_ROLES = [
		('student', 'Student'),
		('admin', 'Admin'),
		('warden', 'Warden'),
		('rector', 'Rector'),
		('maintenance', 'Maintenance'),
		('it', 'IT'),
	]
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	role = models.CharField(max_length=20, choices=USER_ROLES, default='student')

	def __str__(self):
		return f"{self.user.email} - {self.role}"

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
