from rest_framework.permissions import BasePermission

from .models import Project

class IsProjectOwner(BasePermission):
    def has_permission(self, request, view):
        project_id = request.data.get("project")
        if not project_id:
            return False
        
        return Project.objects.filter(
            id=project_id,
            members__user=request.user
        ).exists()
