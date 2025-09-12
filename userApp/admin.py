from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from .models import User, ClientProfile, EmployeeProfile

def is_owner(user):
    # Owner = superuser OR in Owner group
    return user.is_active and (user.is_superuser or user.groups.filter(name="Owner").exists())

def is_admin(user):
    # Admin recognized by group only (avoid confusion with role names)
    return user.is_active and user.groups.filter(name="Admin").exists()

def is_hr(user):
    # HR is a GROUP, not a role
    return user.is_active and user.groups.filter(name="HR").exists()

class ClientProfileInline(admin.StackedInline):
    model = ClientProfile
    fk_name = "user"
    can_delete = False
    extra = 1
    max_num = 1

class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    fk_name = "user"
    can_delete = False
    extra = 1
    max_num = 1

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display  = ("username", "email", "role", "is_staff", "is_superuser", "is_active", "last_login")
    list_filter   = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering      = ("username",)

    # --- Access gates ---
    def has_module_permission(self, request):
        return is_owner(request.user) or is_admin(request.user) or is_hr(request.user)

    def has_view_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user) or is_hr(request.user)

    def has_add_permission(self, request):
        # HR can add Employees; Admin cannot add; Owner can add anyone
        return is_owner(request.user) or is_hr(request.user)

    def has_change_permission(self, request, obj=None):
        if is_owner(request.user):
            return True
        if is_admin(request.user):
            if obj is None:
                return True
            # Admins cannot edit Owners/Admins/superusers
            if obj.is_superuser or obj.role in (User.Roles.OWNER, User.Roles.ADMIN):
                return False
            return True
        if is_hr(request.user):
            if obj is None:
                return True
            # HR can edit only Employees
            return obj.role == User.Roles.EMPLOYEE
        return False

    def has_delete_permission(self, request, obj=None):
        # Only Owner/superuser can delete users
        return is_owner(request.user)

    # --- Scope results ---
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_owner(request.user) or is_admin(request.user):
            return qs
        if is_hr(request.user):
            # HR sees only Employees
            return qs.filter(role=User.Roles.EMPLOYEE)
        return qs.none()

    # --- Forms per role ---
    def get_fieldsets(self, request, obj=None):
        base = list(super().get_fieldsets(request, obj))
        if is_owner(request.user):
            base.append((_('Role'), {"fields": ("role",)}))

        if is_admin(request.user) and not is_owner(request.user):
            # Minimal fields for Admins
            return (
                (None, {"fields": ("username", "password")}),
                (_('Personal info'), {"fields": ("first_name", "last_name", "email")}),
                (_('Important dates'), {"fields": ("last_login", "date_joined")}),
            )

        if is_hr(request.user) and not is_owner(request.user):
            # HR: minimal form; no role/groups/permissions sections
            return (
                (None, {"fields": ("username", "password")}),
                (_('Personal info'), {"fields": ("first_name", "last_name", "email")}),
                (_('Important dates'), {"fields": ("last_login", "date_joined")}),
            )
        return tuple(base)

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            # We'll remove 'role' for HR dynamically in get_form; Owner keeps it
            "fields": ("username", "email", "first_name", "last_name", "password1", "password2", "role"),
        }),
    )

    # --- Read-only protections ---
    def get_readonly_fields(self, request, obj=None):
        ro = set(super().get_readonly_fields(request, obj))
        if not is_owner(request.user):
            ro.update({"is_superuser", "is_staff", "groups", "user_permissions", "last_login", "date_joined"})
        if is_admin(request.user) and not is_owner(request.user):
            ro.add("role")  # Admins can’t change roles
        if is_hr(request.user) and not is_owner(request.user):
            ro.add("role")  # HR won’t edit role; we force EMPLOYEE on save
        return tuple(ro)

    # --- Limit role choices (belt & suspenders) ---
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "role":
            if is_admin(request.user) and not is_owner(request.user):
                kwargs["choices"] = [(User.Roles.EMPLOYEE, "Employee"), (User.Roles.CLIENT, "Client")]
            if is_hr(request.user) and not is_owner(request.user):
                kwargs["choices"] = [(User.Roles.EMPLOYEE, "Employee")]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    # --- Customize add/change form fields dynamically ---
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Hide Groups for non-Owners to prevent escalation
        if not is_owner(request.user) and "groups" in form.base_fields:
            form.base_fields["groups"].queryset = Group.objects.exclude(name__in=["Owner", "Admin"])

        # On ADD view for HR, drop the 'role' field entirely
        if is_hr(request.user) and obj is None and "role" in form.base_fields:
            form.base_fields.pop("role")

        return form

    # Default initial for add form
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        if is_hr(request.user):
            initial["role"] = User.Roles.EMPLOYEE
        return initial

    # --- Enforce policies on save ---
    def save_model(self, request, obj, form, change):
        # HR can only ever save users as EMPLOYEE
        if is_hr(request.user) and not is_owner(request.user):
            obj.role = User.Roles.EMPLOYEE

        # Admins cannot escalate role to Admin/Owner (even via tampered POST)
        if is_admin(request.user) and not is_owner(request.user):
            if obj.role in (User.Roles.ADMIN, User.Roles.OWNER):
                if change:
                    prev = type(obj).objects.get(pk=obj.pk)
                    obj.role = prev.role
                else:
                    obj.role = User.Roles.EMPLOYEE

        super().save_model(request, obj, form, change)
    
    inlines = [ClientProfileInline, EmployeeProfileInline]

    def get_inline_instances(self, request, obj=None):
        """
        - Clients: show ClientProfile inline
        - Employees: show EmployeeProfile inline
        - Admin/Owner: (optional) show EmployeeProfile inline as they are company staff
        - HR should never see client profile inline
        """
        if obj is None:
            return []

        instances = []
        for inline_class in self.inlines:
            if inline_class is ClientProfileInline:
                if obj.role == User.Roles.CLIENT and not is_hr(request.user):
                    instances.append(inline_class(self.model, self.admin_site))
            elif inline_class is EmployeeProfileInline:
                if obj.role in (User.Roles.EMPLOYEE, User.Roles.ADMIN, User.Roles.OWNER):
                    # HR can see/edit employee inline; Admin/Owner too
                    instances.append(inline_class(self.model, self.admin_site))
        return instances



@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "phone", "city", "state_region", "updated_at")
    search_fields = ("user__username", "user__email", "company_name", "phone", "city", "state_region", "postal_code")
    autocomplete_fields = ["user"]
    list_filter = ("country",)
    def has_module_permission(self, request):
        # Hide client profiles from HR
        if is_hr(request.user): return False
        return super().has_module_permission(request)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "job_title", "work_phone", "discord_handle", "updated_at")
    search_fields = ("user__username", "user__email", "job_title", "work_phone", "slack_handle")
    autocomplete_fields = ["user"]
    list_filter = ("city", "state_region", "country")
    # HR allowed here (by default)
