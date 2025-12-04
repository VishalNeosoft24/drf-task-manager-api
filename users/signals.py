from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from .models import User


@receiver(post_save, sender=User)
def assign_role_permission(sender, instance, created, **kwargs):
    if not created:
        return 
    
    if instance.role == "superadmin":
        # give all permissions
        instance.is_superuser = True
        instance.is_staff = True
        instance.save()
    
    elif instance.role == "staff":
        # Give some permissions
        perms = Permission.objects.filter(
            codename__in=['view_project', 'view_task', 'add_task', 'add_project']
        )
        instance.user_permissions.add(*perms)
    
    elif instance.role == "user":
        # Basic read-only access
        perms = Permission.objects.filter(
            codename__in=['view_project', 'view_task']
        )
        instance.user_permissions.add(*perms)
