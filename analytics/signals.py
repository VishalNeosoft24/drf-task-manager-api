"""
Automatic activity logging using Django signals.
This approach automatically logs certain actions without manual intervention.
"""
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from tasks.models import Task, TaskComment
from projects.models import Project, ProjectMember
from .utils import (
    log_task_creation, log_status_change, log_comment,
    log_task_deletion, log_project_creation
)

# Store original values before save
_task_original_values = {}


@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    """Store original task values before save"""
    if instance.pk:
        try:
            original = Task.objects.get(pk=instance.pk)
            _task_original_values[instance.pk] = {
                'status': original.status,
                'assigned_to': original.user,
                'priority': original.priority,
                'title': original.name,
            }
        except Task.DoesNotExist:
            pass


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    """Log task creation and updates automatically"""
    # Skip if no user in thread local (for bulk operations)
    from threading import local
    thread_local = getattr(task_post_save, 'thread_local', None)
    if not thread_local or not hasattr(thread_local, 'user'):
        return

    user = thread_local.user
    
    if created:
        # Log creation
        log_ = log_task_creation(user, instance)
    else:
        # Check for status change
        original = _task_original_values.get(instance.pk, {})
        if original.get('status') and original['status'] != instance.status:
            log_status_change(user, instance, original['status'], instance.status)
        
        # Clean up stored values
        if instance.pk in _task_original_values:
            del _task_original_values[instance.pk]


@receiver(pre_delete, sender=Task)
def task_pre_delete(sender, instance, **kwargs):
    """Log task deletion before it's deleted"""
    from threading import local
    thread_local = getattr(task_pre_delete, 'thread_local', None)
    if thread_local and hasattr(thread_local, 'user'):
        log_task_deletion(thread_local.user, instance)


@receiver(post_save, sender=TaskComment)
def comment_post_save(sender, instance, created, **kwargs):
    """Log comment creation"""
    if created:
        from threading import local
        thread_local = getattr(comment_post_save, 'thread_local', None)
        if thread_local and hasattr(thread_local, 'user'):
            # Use comment's user if no thread local user
            user = getattr(thread_local, 'user', instance.user)
            log_comment(user, instance.task, instance)


@receiver(post_save, sender=Project)
def project_post_save(sender, instance, created, **kwargs):
    """Log project creation"""
    if created:
        log_project_creation(instance.created_by, instance)
