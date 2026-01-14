from django.db import models
from users.models import User
from projects.models import Project
from tasks.models import Task

class ActivityLog(models.Model):
    """Track all activities in projects and tasks"""
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('assign', 'Assigned'),
        ('comment', 'Commented'),
        ('status_change', 'Status Changed'),
        ('member_add', 'Member Added'),
        ('member_remove', 'Member Removed'),
        ('member_role_change', 'Member Role Changed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Store additional metadata as JSON
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['task', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"