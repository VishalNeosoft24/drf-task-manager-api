from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    GLOBAL_ROLES = [
        ('superadmin', 'Super Admin'),
        ('staff', 'Staff'),
        ('user', 'User'),
    ]

    JOB_ROLES = [
        ('backend_dev', 'Backend Developer'),
        ('frontend_dev', 'Frontend Developer'),
        ('fullstack_dev', 'Fullstack Developer'),
        ('qa', 'QA Tester'),
        ('devops', 'DevOps Engineer'),
        ('uiux', 'UI/UX Designer'),
        ('pm', 'Project Manager'),
        ('tl', 'Team Lead'),
        ('architect', 'Software Architect'),
        ('intern', 'Intern'),
    ]
    
    role = models.CharField(max_length=50, choices=GLOBAL_ROLES, default='user')
    job_role = models.CharField(max_length=50, choices=JOB_ROLES, blank=True, null=True)
    
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)

    phone_numer = models.CharField(max_length=15, blank=True, null=True) # Typo in field name retained as per original request
    profile_picture = models.ImageField(upload_to='porfiles/', blank=True, null=True) # Typo in folder name retained as per original request
    date_of_joining = models.DateField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} ({self.last_name}) - {self.username}"
