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