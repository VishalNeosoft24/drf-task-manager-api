from .models import ActivityLog

def log_activity(user, project, action, description, task=None, metadata=None):
    """
    Helper function to create activity log entries.
    
    Args:
        user: User performing the action
        project: Project where action occurred
        action: Action type (from ACTION_CHOICES)
        description: Human-readable description
        task: Optional task reference
        metadata: Optional dict with additional data
    
    Returns:
        ActivityLog instance
    """
    return ActivityLog.objects.create(
        user=user,
        project=project,
        task=task,
        action=action,
        description=description,
        metadata=metadata
    )


def log_project_creation(user, project):
    """Log project creation"""
    return log_activity(
        user=user,
        project=project,
        action='create',
        description=f'Created project "{project.name}"',
        metadata={'project_id': project.id}
    )


def log_project_update(user, project, changes):
    """Log project updates with change details"""
    change_list = ', '.join([f'{k}: {v[0]} → {v[1]}' for k, v in changes.items()])
    return log_activity(
        user=user,
        project=project,
        action='update',
        description=f'Updated project: {change_list}',
        metadata={'changes': changes}
    )


def log_task_creation(user, task):
    """Log task creation"""
    return log_activity(
        user=user,
        project=task.project,
        task=task,
        action='create',
        description=f'Created task "{task.name}"',
        metadata={
            'task_id': task.id,
            'status': task.status,
            'priority': task.priority
        }
    )


def log_task_update(user, task, changes):
    """Log task updates"""
    change_list = ', '.join([f'{k}: {v[0]} → {v[1]}' for k, v in changes.items()])
    return log_activity(
        user=user,
        project=task.project,
        task=task,
        action='update',
        description=f'Updated task "{task.name}": {change_list}',
        metadata={'changes': changes}
    )


def log_task_assignment(user, task, assignee, previous_assignee=None):
    """Log task assignment"""
    if previous_assignee:
        description = f'Reassigned task "{task.name}" from {previous_assignee.username} to {assignee.username}'
    else:
        description = f'Assigned task "{task.name}" to {assignee.username}'
    
    return log_activity(
        user=user,
        project=task.project,
        task=task,
        action='assign',
        description=description,
        metadata={
            'assignee_id': assignee.id,
            'assignee_username': assignee.username,
            'previous_assignee_id': previous_assignee.id if previous_assignee else None
        }
    )


def log_status_change(user, task, old_status, new_status):
    """Log task status change"""
    return log_activity(
        user=user,
        project=task.project,
        task=task,
        action='status_change',
        description=f'Changed status of "{task.name}" from {old_status} to {new_status}',
        metadata={
            'old_status': old_status,
            'new_status': new_status
        }
    )


def log_comment(user, task, comment):
    """Log comment creation"""
    preview = comment.comment[:50] + '...' if len(comment.comment) > 50 else comment.comment
    return log_activity(
        user=user,
        project=task.project,
        task=task,
        action='comment',
        description=f'Commented on "{task.name}": {preview}',
        metadata={'comment_id': comment.id}
    )


def log_task_deletion(user, task):
    """Log task deletion"""
    return log_activity(
        user=user,
        project=task.project,
        task=None,  # Task will be deleted
        action='delete',
        description=f'Deleted task "{task.name}"',
        metadata={
            'task_name': task.name,
            'task_status': task.status
        }
    )


def log_member_added(user, project, new_member, role):
    """Log member addition"""
    return log_activity(
        user=user,
        project=project,
        action='member_add',
        description=f'Added {new_member.username} as {role}',
        metadata={
            'member_id': new_member.id,
            'member_username': new_member.username,
            'role': role
        }
    )


def log_member_removed(user, project, removed_member):
    """Log member removal"""
    return log_activity(
        user=user,
        project=project,
        action='member_remove',
        description=f'Removed {removed_member.username} from project',
        metadata={
            'member_id': removed_member.id,
            'member_username': removed_member.username
        }
    )


def log_member_role_change(user, project, member, old_role, new_role):
    """Log member role change"""
    return log_activity(
        user=user,
        project=project,
        action='member_role_change',
        description=f'Changed {member.username}\'s role from {old_role} to {new_role}',
        metadata={
            'member_id': member.id,
            'member_username': member.username,
            'old_role': old_role,
            'new_role': new_role
        }
    )
