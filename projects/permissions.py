from rest_framework.permissions import BasePermission

from .models import Project, ProjectMember

class IsProjectOwner(BasePermission):
    def get_project_id(self, request, view):
        # Case 1: URL project_id
        if "project_id" in view.kwargs:
            return view.kwargs["project_id"]

        # Case 2: project inside request.data (POST)
        return request.data.get("project")
    
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        
        project_id = self.get_project_id(request, view)

        if not project_id:
            return False

        # Check if the user is an owner of the project
        return ProjectMember.objects.filter(
            project_id=project_id,
            user=request.user,
            role='owner'
        ).exists()


class CanCreateProject(BasePermission):
    message = "You don't have permission to create project."

    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.has_perm("projects.add_project")
        return True

class CanUpdateDeleteProject(BasePermission):
    message = "You don't have permission to perform this action."

    def has_permission(self, request, view):
        if request.method not in ["DELETE", "PATCH", "PUT"]:
            return True

        user = request.user
        project_id = view.kwargs.get("pk")

        return (
            user.is_superuser or
            user.is_staff or 
            ProjectMember.objects.filter(
                project_id=project_id,
                user=user,
                role="owner"
            ).exists()
        )
