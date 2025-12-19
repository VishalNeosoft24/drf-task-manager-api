
from django.db.models import Q
from ..models import Task
from .search_tasks_func import search_tasks   


def get_base_tasks_queryset(user):
    """
    Return base queryset based on user role
    """
    if user.is_staff or user.is_superuser:
        return Task.objects.all()
    return Task.objects.filter(user=user)


def apply_task_filters(tasks, params):
    """
    Apply query param based filters
    """
    status = params.get("status")
    project = params.get("project")
    priority = params.get("priority")
    search = params.get("search")

    if status:
        tasks = tasks.filter(status=status)

    if project:
        tasks = tasks.filter(project_id=project)

    if priority:
        tasks = tasks.filter(priority=priority)

    if search:
        tasks = search_tasks(tasks, search)

    return tasks
