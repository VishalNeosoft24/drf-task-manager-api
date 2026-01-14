from projects.models import ProjectMember
from .global_permissions import GLOBAL_PERMISSION
from .project_role_permissions import PROJECT_ROLE_PERMISSION

def get_user_permissions(user, project):
    # 1. GLOBAL ROLE
    global_perms = GLOBAL_PERMISSION.get(user.role, {})

    # If superadmin -> full permissions
    if user.role == "superadmin":
        return global_perms

    # 2. Check if user is project member
    try:
        member = ProjectMember.objects.get(user=user, project=project)
        project_role = member.role
    except ProjectMember.DoesNotExist:
        # Not a member → return ONLY global permissions
        return global_perms

    project_perms = PROJECT_ROLE_PERMISSION[project_role]

    # 3. Combine → OR logic (True wins)
    final = {key: (global_perms.get(key, False) or project_perms.get(key, False)) for key in project_perms.keys()}

    return final
