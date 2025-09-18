import uuid
from django.db import models
from accounts.models import User
# Create your models here.

class Categories(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Jobs(models.Model):
    WORKING_AREA_CHOICES = [
        ('onsite', 'Onsite'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]
    LONGEVITY_CHOICES = [
        ('contractual', 'Contractual'),
        ('permanent', 'Permanent'),
    ]
    TYPE_CHOICES = [
        ('full-time', 'Full-Time'),
        ('part-time', 'Part-Time')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    location =  models.CharField(max_length=100)
    working_area = models.CharField(max_length=20, choices=WORKING_AREA_CHOICES)
    longevity = models.CharField(max_length=15, choices=LONGEVITY_CHOICES)
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.id})" 

class Applications(models.Model):
    STATUS_CHOICE = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_applications')
    status = models.CharField(max_length=10, choices=STATUS_CHOICE, default='pending')
    resume = models.TextField(null=False, blank=False)
    cover_letter = models.TextField(null=False, blank=False)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.job} -> {self.user}"
    
class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, related_name='application')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.message}"
    