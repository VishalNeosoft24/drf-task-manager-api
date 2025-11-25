from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    message = "You must be the owner or an admin to access this."

    def has_object_permission(self, request, view, obj):
        return bool(request.user and (request.user.is_staff or request.user.pk==obj.pk))