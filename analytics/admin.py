from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'project', 'task', 'created_at']
    list_filter = ['action', 'created_at', 'project']
    search_fields = ['description', 'user__username', 'project__name', 'task__title']
    readonly_fields = ['user', 'project', 'task', 'action', 'description', 'created_at', 'metadata']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        # Activities should only be created programmatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Activities should not be modified
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete activity logs
        return request.user.is_superuser

