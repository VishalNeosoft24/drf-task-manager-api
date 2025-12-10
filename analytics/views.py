from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.functions import TruncDay
from django.utils.timezone import now, timedelta
from tasks.models import Task
from django.db.models import Count


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def task_status_chart(request):
    data = [
        { "name": "To Do", "value": Task.objects.filter(status="todo").count()},
        { "name": "In Progress", "value": Task.objects.filter(status="progress").count()},
        { "name": "Completed", "value": Task.objects.filter(status="done").count()},
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def task_weekly_chart(request):
    today = now().date()
    last_week = today - timedelta(days=6)

    queryset = (
        Task.objects.filter(created_at__date__gte=last_week)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(tasks=Count("id"))
        .order_by("day")
    )

    data = [
        {"name": item["day"].strftime("%a"), "tasks": item["tasks"]}
        for item in queryset
    ]

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def project_task_summary(request, project_id):
    tasks = Task.objects.filter(project_id=project_id)
    summary = {
        "total_tasks": tasks.count(),
        "todo_tasks": tasks.filter(status="todo").count(),
        "in_progress_tasks": tasks.filter(status="progress").count(),
        "completed_tasks": tasks.filter(status="done").count(),
    }
    return Response(summary)