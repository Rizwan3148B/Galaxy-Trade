from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Stock

class CustomUserAdmin(UserAdmin):
    """
    We create a custom admin class to tell Django to display 
    our custom fields alongside the default ones.
    """
    # 1. This adds virtual_cash to the columns on the main list page you are looking at
    list_display = ('username', 'email', 'is_staff', 'virtual_cash')
    
    # 2. This adds a new section to the edit screen when you click on a specific user
    fieldsets = UserAdmin.fieldsets + (
        ('Paper Trading Info', {'fields': ('virtual_cash', 'profile_pic')}),
    )

# Register our models with the new CustomUserAdmin
admin.site.register(User, CustomUserAdmin)
admin.site.register(Stock)