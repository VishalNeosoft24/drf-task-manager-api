from rest_framework.serializers import ModelSerializer, Serializer, PrimaryKeyRelatedField

from users.models import User
from .models import Task, TaskComment
from projects.models import Project
from users.serializers import UserSerializer


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id','name']
        read_only_fields = ['id']


class TaskSerializer(ModelSerializer):
    # user = PrimaryKeyRelatedField(write_only=True, queryset=User.objects.all())
    project = PrimaryKeyRelatedField(write_only=True, queryset=Project.objects.all())

    user_details = UserSerializer(source='user', read_only=True)
    project_details = ProjectSerializer(source='project', read_only=True)

    class Meta:
        model = Task
        fields  = [
            'id',
            'name',
            'description',
            'attachment',
            # 'user',
            'project',
            'user_details',
            'project_details',
            'status',
            'priority',
            'created_at',
            'updated_at',
            'due_date',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            # 'user': {'write_only': True},
            'project': {'write_only': True},
        }

    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        task = Task.objects.create(**validated_data)
        task.save()
        return task
    
    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field != "user":   # Prevent ownership change
                setattr(instance, field, value)
        instance.save()
        return instance
