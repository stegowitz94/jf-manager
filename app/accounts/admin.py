from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("JF-Manager", {"fields": ("role", "supervisor")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("JF-Manager", {"fields": ("role", "supervisor")}),)
    list_display = ("username", "email", "first_name", "last_name", "role", "supervisor", "is_staff", "is_active")
