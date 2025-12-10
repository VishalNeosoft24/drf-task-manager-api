from django.urls import path
from . import views

urlpatterns = [
    # Define your analytics app URL patterns here
    path('task-status-chart/', views.task_status_chart, name='task_status_chart'),
    path('task-weekly-chart/', views.task_weekly_chart, name='task_weekly_chart'),
    path('project-task-summary/<int:project_id>/', views.project_task_summary, name='project_task_summary'),
]