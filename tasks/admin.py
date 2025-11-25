from django.contrib import admin
from .models import Task, TaskComment

# Register your models here.
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description',
        'attachment',
        'user',
        'project',
        'status',
        'priority',
        'created_at',
        'updated_at',
        'due_date',
    ]
    list_filter = ['user', 'status', 'priority', 'project']
    search_fields = ['user', 'project']

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'task',
        'user',
        'comment',
        'created_at',
    ]
    list_filter = ['user']
    search_fields = ['user', 'task', 'comment']