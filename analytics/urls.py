from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'activities', views.ActivityLogViewSet, basename='activity')

urlpatterns = [
    # Define your analytics app URL patterns here
    path('task-status-chart/', views.task_status_chart, name='task_status_chart'),
    path('task-weekly-chart/', views.task_weekly_chart, name='task_weekly_chart'),
    path('project-task-summary/<int:project_id>/', views.project_task_summary, name='project_task_summary'),
    path('', include(router.urls)),

]