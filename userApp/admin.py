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
        "company", "company_name", "company_email", "phone",
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

    # we’ll attach inlines dynamically via get_inline_instances()
    inlines = [ClientProfileInline, EmployeeProfileInline]

    # ---- module visibility ----
    def has_module_permission(self, request):
        # Allow all staff (Owner/Admin/HR/Employee) to enter the Users app
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    # ---- add / change / delete ----
    def has_add_permission(self, request):
        # For now: only Owner may add users (you can allow HR later if desired)
        return is_owner(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user)

    def has_change_permission(self, request, obj=None):
        # Owner/Admin can edit everyone (Admin blocked from touching Owners/Admins below)
        if is_owner(request.user):
            return True
        if is_admin(request.user):
            if obj is None:
                return True
            # Admins cannot edit Owners/Admins/superusers
            if obj.is_superuser or obj.role in (User.Roles.OWNER, User.Roles.ADMIN):
                return False
            return True

        # HR & plain staff: can only open THEIR OWN user page (to change password)
        if is_plain_staff(request.user):
            if obj is None:
                return True
            return obj.pk == request.user.pk

        return False

    # ---- scope queryset ----
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if is_owner(request.user) or is_admin(request.user):
            return qs

        if is_hr(request.user):
            # HR: see Employees + self (so they can reach their own password form)
            return qs.filter(Q(role=User.Roles.EMPLOYEE) | Q(pk=request.user.pk))

        if is_plain_staff(request.user):
            # Plain employees: only themselves
            return qs.filter(pk=request.user.pk)

        return qs.none()

    # ---- lock down fields ----
    def get_readonly_fields(self, request, obj=None):
        ro = set(super().get_readonly_fields(request, obj))
        # Nobody but Owner can touch permissions-related fields
        if not is_owner(request.user):
            ro.update({"is_superuser", "is_staff", "groups", "user_permissions", "last_login", "date_joined"})
        # Admin cannot change role
        if is_admin(request.user) and not is_owner(request.user):
            ro.add("role")
        # HR & plain staff: everything read-only (they’ll use "change password" only)
        if is_plain_staff(request.user):
            ro.update({"username", "first_name", "last_name", "email", "role"})
        return tuple(ro)

    # Slimmer forms for non-owners
    def get_fieldsets(self, request, obj=None):
        if is_owner(request.user):
            base = list(super().get_fieldsets(request, obj))
            base.append((_('Role'), {"fields": ("role",)}))
            return tuple(base)

        # Minimal form for Admin/HR/Employees (all read-only except password link)
        return (
            (None, {"fields": ("username", "password")}),
            (_('Personal info'), {"fields": ("first_name", "last_name", "email")}),
            (_('Important dates'), {"fields": ("last_login", "date_joined")}),
        )

    # Prevent non-owners from assigning sensitive groups
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not is_owner(request.user) and "groups" in form.base_fields:
            form.base_fields["groups"].queryset = Group.objects.exclude(name__in=["Owner", "Admin"])
        return form

    # Decide which inlines to show to whom
    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        # Plain staff looking at themselves: hide inlines (password-only)
        if is_plain_staff(request.user) and obj.pk == request.user.pk:
            return []
        instances = []
        # Show ClientProfile inline only when target user is a CLIENT; hide from HR
        if obj.role == User.Roles.CLIENT and not is_hr(request.user):
            instances.append(ClientProfileInline(self.model, self.admin_site))
        # Show EmployeeProfile inline when target user is company-side (Emp/Admin/Owner)
        if obj.role in (User.Roles.EMPLOYEE, User.Roles.ADMIN, User.Roles.OWNER):
            # HR can see this inline for others, not for themselves
            if not (is_hr(request.user) and obj.pk == request.user.pk):
                instances.append(EmployeeProfileInline(self.model, self.admin_site))
        return instances


# ---- ClientProfile & EmployeeProfile admins ----

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "company_name", "phone", "city", "state_region", "updated_at")
    search_fields = ("user__username", "user__email", "company__name", "company_name", "phone", "city", "state_region", "postal_code")
    autocomplete_fields = ["user", "company"]
    readonly_fields = ("image_preview",)

    fields = (
        "user",
        "profile_image", "image_preview",
        "company",
        "company_name", "company_email", "phone",
        "address_line1", "address_line2", "city", "state_region", "postal_code", "country",
        "created_at", "updated_at",
    )
    readonly_fields += ("created_at", "updated_at")

    def image_preview(self, obj):
        if obj and obj.profile_image:
            return format_html('<img src="{}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;" />', obj.profile_image.url)
        return "—"
    image_preview.short_description = "Preview"

    # Keep HR out of client profiles (view or edit)
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
        # Only staff may see; clients cannot. HR may see.
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        # Keep adds to Owner/Admin for now
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user):
            return True
        if is_hr(request.user):
            if obj is None:
                return True
            # HR can edit employee profiles except their own
            return obj.user_id != request.user.id
        # Plain staff cannot edit EmployeeProfile in admin
        return False

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user)
