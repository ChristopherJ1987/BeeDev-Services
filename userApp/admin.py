# userApp/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.utils.html import format_html

from .models import User, ClientProfile, EmployeeProfile

# ---- helpers ----
def is_owner(u):  # superuser OR Owner group
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):  # Admin group
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):     # HR group
    return u.is_active and u.groups.filter(name="HR").exists()

def is_plain_staff(u):  # staff but not Owner/Admin (HR counts as plain staff here)
    return u.is_active and u.is_staff and not is_owner(u) and not is_admin(u)

# ---- Inlines ----
class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    fk_name = "user"
    can_delete = False
    extra = 0
    max_num = 1
    readonly_fields = ("image_preview",)

    fields = (
        "profile_image", "image_preview",
        # removed: "company",
        "company_name", "company_email", "phone",
        "address_line1", "address_line2", "city", "state_region", "postal_code", "country",
    )

    def image_preview(self, obj):
        if obj and obj.profile_image:
            return format_html('<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" />', obj.profile_image.url)
        return "—"
    image_preview.short_description = "Preview"


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    fk_name = "user"
    can_delete = False
    extra = 0
    max_num = 1
    readonly_fields = ("image_preview",)

    fields = (
        "profile_image", "image_preview",
        "job_title", "work_email", "work_phone", "discord_handle",
        "address_line1", "address_line2", "city", "state_region", "postal_code", "country",
        "notes_internal",
    )

    def image_preview(self, obj):
        if obj and obj.profile_image:
            return format_html('<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" />', obj.profile_image.url)
        return "—"
    image_preview.short_description = "Preview"


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display  = ("username", "email", "role", "is_staff", "is_superuser", "is_active", "last_login")
    list_filter   = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering      = ("username",)
    inlines = [ClientProfileInline, EmployeeProfileInline]

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return is_owner(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user)

    def has_change_permission(self, request, obj=None):
        if is_owner(request.user):
            return True
        if is_admin(request.user):
            if obj is None:
                return True
            if obj.is_superuser or obj.role in (User.Roles.OWNER, User.Roles.ADMIN):
                return False
            return True
        if is_plain_staff(request.user):
            if obj is None:
                return True
            return obj.pk == request.user.pk
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_owner(request.user) or is_admin(request.user):
            return qs
        if is_hr(request.user):
            return qs.filter(Q(role=User.Roles.EMPLOYEE) | Q(pk=request.user.pk))
        if is_plain_staff(request.user):
            return qs.filter(pk=request.user.pk)
        return qs.none()

    def get_readonly_fields(self, request, obj=None):
        ro = set(super().get_readonly_fields(request, obj))
        if not is_owner(request.user):
            ro.update({"is_superuser", "is_staff", "groups", "user_permissions", "last_login", "date_joined"})
        if is_admin(request.user) and not is_owner(request.user):
            ro.add("role")
        if is_plain_staff(request.user):
            ro.update({"username", "first_name", "last_name", "email", "role"})
        return tuple(ro)

    def get_fieldsets(self, request, obj=None):
        if is_owner(request.user):
            base = list(super().get_fieldsets(request, obj))
            base.append((_('Role'), {"fields": ("role",)}))
            return tuple(base)
        return (
            (None, {"fields": ("username", "password")}),
            (_('Personal info'), {"fields": ("first_name", "last_name", "email")}),
            (_('Important dates'), {"fields": ("last_login", "date_joined")}),
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not is_owner(request.user) and "groups" in form.base_fields:
            form.base_fields["groups"].queryset = Group.objects.exclude(name__in=["Owner", "Admin"])
        return form

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        if is_plain_staff(request.user) and obj.pk == request.user.pk:
            return []
        instances = []
        if obj.role == User.Roles.CLIENT and not is_hr(request.user):
            instances.append(ClientProfileInline(self.model, self.admin_site))
        if obj.role in (User.Roles.EMPLOYEE, User.Roles.ADMIN, User.Roles.OWNER):
            if not (is_hr(request.user) and obj.pk == request.user.pk):
                instances.append(EmployeeProfileInline(self.model, self.admin_site))
        return instances


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "phone", "city", "state_region", "updated_at")
    search_fields = ("user__username", "user__email", "company_name", "phone", "city", "state_region", "postal_code")
    autocomplete_fields = ["user"]
    readonly_fields = ("image_preview", "created_at", "updated_at")

    fields = (
        "user",
        "profile_image", "image_preview",
        # removed: "company",
        "company_name", "company_email", "phone",
        "address_line1", "address_line2", "city", "state_region", "postal_code", "country",
        "created_at", "updated_at",
    )

    def image_preview(self, obj):
        if obj and obj.profile_image:
            return format_html('<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" />', obj.profile_image.url)
        return "—"
    image_preview.short_description = "Preview"

    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "job_title", "work_phone", "discord_handle", "updated_at")
    search_fields = ("user__username", "user__email", "job_title", "work_phone", "discord_handle")
    autocomplete_fields = ["user"]
    readonly_fields = ("image_preview", "created_at", "updated_at")

    fields = (
        "user",
        "profile_image", "image_preview",
        "job_title", "work_email", "work_phone", "discord_handle",
        "address_line1", "address_line2", "city", "state_region", "postal_code", "country",
        "notes_internal",
        "created_at", "updated_at",
    )

    def image_preview(self, obj):
        if obj and obj.profile_image:
            return format_html('<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" />', obj.profile_image.url)
        return "—"
    image_preview.short_description = "Preview"

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user):
            return True
        if is_hr(request.user):
            if obj is None:
                return True
            return obj.user_id != request.user.id
        return False

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user)
