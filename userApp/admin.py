from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User

HR_GROUP_NAME = "HR"

def is_hr(user):
    return user.is_active and user.groups.filter(name=HR_GROUP_NAME).exists()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser", "is_active")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    # Visibility / access
    def has_module_permission(self, request):
        return request.user.is_superuser or is_hr(request.user)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or is_hr(request.user)

    def has_add_permission(self, request):
        # HR can add clients; superusers can add anyone
        return request.user.is_superuser or is_hr(request.user)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or is_hr(request.user)

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete users
        return request.user.is_superuser

    # HR should see only CLIENT users
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if is_hr(request.user):
            return qs.filter(role=User.Roles.CLIENT)
        return qs.none()

    # Lock down sensitive fields for HR
    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser:
            ro += ("is_superuser", "is_staff", "groups", "user_permissions", "last_login", "date_joined")
        return ro

    # HR can only set role=CLIENT when adding/editing
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "role" and is_hr(request.user):
            kwargs["choices"] = [(User.Roles.CLIENT, "Client")]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    # Belt-and-suspenders: enforce CLIENT role for HR on save
    def save_model(self, request, obj, form, change):
        if is_hr(request.user) and obj.role != User.Roles.CLIENT:
            obj.role = User.Roles.CLIENT
        super().save_model(request, obj, form, change)
