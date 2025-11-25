from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    message = "You must be the owner of this task."

    def has_object_permission(self, request, view, obj):
        # return obj.user == request.user
        return bool(request.user and (request.user.pk==obj.user.pk or request.user.is_staff or request.user.is_superuser))
