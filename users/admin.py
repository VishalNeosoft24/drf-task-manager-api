from django.contrib import admin
from .models import User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 
        'first_name',
        'last_name',
        'email',
        'role', 
        'phone_numer', 
        'department', 
        'designation', 
        'profile_picture', 
        'date_of_joining', 
        'last_seen', 
        'is_online', 
        'email_verified',
    ]
    list_filter = ['role']
    search_fields = ['username', 'phone_number']
    
