from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, filters
from django.db.models.functions import TruncDay
from django.utils.timezone import now, timedelta
from tasks.models import Task
from django.db.models import Count
from django.utils import timezone
from .models import ActivityLog
from .serializers import ActivityLogSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def task_status_chart(request):
    if request.user.is_staff or request.user.is_superuser:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(user=request.user)

    data = [
        { "name": "To Do", "value": tasks.filter(status="todo").count()},
        { "name": "In Progress", "value": tasks.filter(status="progress").count()},
        { "name": "Completed", "value": tasks.filter(status="done").count()},
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
    if request.user.is_staff or request.user.is_superuser  or request.user.role in ["owner", "admin"]:
        project_tasks_summary = Task.objects.filter(project_id=project_id)
        user_task_summary = Task.objects.filter(project_id=project_id, user=request.user)

        project_summary = {
            "total_tasks": project_tasks_summary.count(),
            "todo_tasks": project_tasks_summary.filter(status="todo").count(),
            "in_progress_tasks": project_tasks_summary.filter(status="progress").count(),
            "completed_tasks": project_tasks_summary.filter(status="done").count(),
        }

    else:
        user_task_summary = Task.objects.filter(user=request.user, project_id=project_id)

    user_summary = {
        "total_tasks": user_task_summary.count(),
        "todo_tasks": user_task_summary.filter(status="todo").count(),
        "in_progress_tasks": user_task_summary.filter(status="progress").count(),
        "completed_tasks": user_task_summary.filter(status="done").count(),
    }
    return Response({
        "project_summary": project_summary if 'project_summary' in locals() else None,
        "user_summary": user_summary
    })  


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing activity logs.
    Read-only - activities are created automatically.
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Users see only activities from their projects"""
        user = self.request.user
        
        if user.is_superadmin():
            queryset = ActivityLog.objects.all()
        else:
            # Get projects where user is a member
            project_ids = user.project_memberships.values_list('project_id', flat=True)
            queryset = ActivityLog.objects.filter(project_id__in=project_ids)
        
        # Apply filters
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Date range filters
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.select_related('user', 'project', 'task')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities (last 24 hours)"""
        yesterday = timezone.now() - timedelta(days=1)
        activities = self.get_queryset().filter(created_at__gte=yesterday)
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_activities(self, request):
        """Get activities performed by current user"""
        activities = self.get_queryset().filter(user=request.user)
        
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get activity statistics for a project"""
        project_id = request.query_params.get('project')
        
        if not project_id:
            return Response({'error': 'project parameter required'}, status=400)
        
        queryset = self.get_queryset().filter(project_id=project_id)
        
        # Count by action type
        action_counts = {}
        for action, _ in ActivityLog.ACTION_CHOICES:
            action_counts[action] = queryset.filter(action=action).count()
        
        # Most active users
        from django.db.models import Count
        active_users = queryset.values(
            'user__id', 'user__username', 'user__first_name', 'user__last_name'
        ).annotate(
            activity_count=Count('id')
        ).order_by('-activity_count')[:5]
        
        # Activities by day (last 7 days)
        from django.db.models.functions import TruncDate
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_activities = queryset.filter(
            created_at__gte=seven_days_ago
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return Response({
            'action_counts': action_counts,
            'most_active_users': list(active_users),
            'daily_activities': list(daily_activities),
            'total_activities': queryset.count()
        })
