from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from users.models import User
from .models import Project, ProjectMember

class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'created_at', 'description', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        request = self.context['request']
        project = Project.objects.create(**validated_data)
        ProjectMember.objects.create(user=request.user, project=project)
        return project


class ProjectMemberAddSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=User.objects.all())
    project = PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = ProjectMember
        fields = ['project', 'user']

    def create(self, validated_data):
        return ProjectMember.objects.create(**validated_data)
