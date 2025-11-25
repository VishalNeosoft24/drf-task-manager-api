from django.core.management.base import BaseCommand

from users.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        for user in User.objects.all():
            if not user.password.startswith("pbkdf2_"):
                print(f"Fixing Password for {user.username}")
                raw_password = user.password
                user.set_password(raw_password=raw_password)
                user.save()