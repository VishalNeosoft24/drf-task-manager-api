from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, SerializerMethodField
from django.contrib.auth.models import Permission
from users.models import User
from .models import Project, ProjectMember

class ProjectSerializer(ModelSerializer):
    user_role = SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id', 'name', 'created_at', 'description', 'updated_at', 'user_role']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        request = self.context['request']
        project = Project.objects.create(**validated_data, created_by=request.user)
        ProjectMember.objects.create(user=request.user, project=project, role='owner')
        return project

    def get_user_role(self, obj):
        request = self.context.get('request')
        if not request:
            return None

        membership = ProjectMember.objects.filter(
            user=request.user,
            project=obj
        ).first()

        return membership.role if membership else None


class ProjectMemberAddSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    project = PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = ProjectMember
        fields = ['project', 'user', 'role']
        read_only_fields = ['role']

    def create(self, validated_data):
        return ProjectMember.objects.create(**validated_data)
