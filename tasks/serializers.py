from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, HiddenField, CurrentUserDefault, ValidationError

from users.models import User
from .models import Task, TaskComment
from projects.models import Project, ProjectMember
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
        user = self.context['request'].user
        validated_data['user'] = user
        project = validated_data['project']
        is_member = ProjectMember.objects.filter(project=project, user=user).exists()

        if not is_member:
            raise ValidationError(
                {"message": "You are not a member of this project."}
            )

        task = Task.objects.create(**validated_data)
        task.save()
        return task
    
    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            if field != "user":   # Prevent ownership change
                setattr(instance, field, value)
        instance.save()
        return instance


class CommentSerializer(ModelSerializer):
    task = PrimaryKeyRelatedField(write_only = True, queryset = Task.objects.all())
    user = HiddenField(default=CurrentUserDefault())

    task_details = TaskSerializer(source='task', read_only=True)
    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'user', 'task_details', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


    def create(self, validated_data):
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data.pop('task', None)
        return super().update(instance, validated_data)