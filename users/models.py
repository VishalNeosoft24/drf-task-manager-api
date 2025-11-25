from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    choices=[
        ('admin', 'Admin'),
        ('manager', 'Project Manager'), 
        ('lead', 'Team Lead'), 
        ('developer', 'Developer'), 
        ('client', 'Client')
    ]
    
    role = models.CharField(max_length=50, choices=choices, default='developer')
    phone_numer = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='porfiles/', blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
