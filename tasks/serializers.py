from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, HiddenField, CurrentUserDefault, ValidationError, SerializerMethodField

from projects.permissions_constant.permission_utils import get_user_permissions
from users.models import User
from .models import Task, TaskComment
from projects.models import Project, ProjectMember
from users.serializers import UserSerializer


class ProjectSerializer(ModelSerializer):
    permissions = SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id','name', 'permissions']
        read_only_fields = ['id']

    def get_permissions(self, obj):
        request = self.context.get("request")
        if not request:
            return {}
        return get_user_permissions(request.user, obj)

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
        project = validated_data['project']

        # SUPERADMIN -> allowed without membership
        if user.is_superuser:
            return Task.objects.create(**validated_data, user=user)

        # STAFF -> allowed but DO NOT auto add to ProjectMember
        if user.is_staff:
            return Task.objects.create(**validated_data, user=user)

        # NORMAL USERS -> must be project members
        is_member = ProjectMember.objects.filter(project=project, user=user).exists()

        if not is_member:
            raise ValidationError(
                {"message": "You are not a member of this project."}
            )

        return Task.objects.create(**validated_data, user=user)
    
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