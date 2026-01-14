from rest_framework import serializers
from .models import ActivityLog
from users.models import User

class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    task_title = serializers.CharField(source='task.title', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'project', 'project_name', 'task', 'task_title',
            'action', 'action_display', 'description', 'created_at', 'metadata'
        ]
        read_only_fields = ['created_at']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }
