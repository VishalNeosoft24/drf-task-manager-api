from rest_framework.permissions import BasePermission

from projects.models import ProjectMember

class IsOwnerOrAdmin(BasePermission):
    message = "You must be the owner of this task."

    def has_object_permission(self, request, view, obj):
        # return obj.user == request.user
        return bool(request.user and (request.user.pk==obj.user.pk or request.user.is_staff or request.user.is_superuser))


class IsOwner(BasePermission):
    message = "You must be the owner of this task."
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class CreateTaskPermission(BasePermission):
    message = "viewr has no permission to create a task"
    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        
        project = request.data.get("project")

        if not project:
            return False

        member = ProjectMember.objects.filter(project=project, user=request.user).first()
        if not member:
            return False
        
        allowed = ("owner", "admin", "member")

        return member.role in allowed
