from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import User, ClientProfile, EmployeeProfile  # if you added EmployeeProfile; otherwise remove

def is_owner(user):
    return user.is_active and (user.is_superuser or user.groups.filter(name="Owner").exists())

def is_admin(user):
    return user.is_active and user.groups.filter(name="Admin").exists()

def is_hr(user):
    return user.is_active and user.groups.filter(name="HR").exists()

def is_employee(user):
    # Treat pure employees (not Owner/Admin/HR) as Employee
    return (
        user.is_active
        and not user.is_superuser
        and not user.groups.filter(name__in=["Owner", "Admin", "HR"]).exists()
        and (getattr(user, "role", None) == User.Roles.EMPLOYEE or user.groups.filter(name="Employee").exists())
    )

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

    inlines = [ClientProfileInline, EmployeeProfileInline]

    # ----- Access gates -----
    def has_module_permission(self, request):
        # Allow Employees into the Users app
        return is_owner(request.user) or is_admin(request.user) or is_hr(request.user) or is_employee(request.user)

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        # Owner or HR can add; Admin/Employee cannot
        return is_owner(request.user) or is_hr(request.user)

    def has_change_permission(self, request, obj=None):
        if is_owner(request.user):
            return True
        if is_admin(request.user):
            if obj is None:
                return True
            if obj.is_superuser or obj.role in (User.Roles.OWNER, User.Roles.ADMIN):
                return False
            return True
        if is_hr(request.user):
            if obj is None:
                return True
            return obj.role == User.Roles.EMPLOYEE
        if is_employee(request.user):
            if obj is None:
                return True  # needed to open the changelist
            # Employee can edit ONLY their own record
            return (obj.pk == request.user.pk) or (obj.role == User.Roles.CLIENT)
        return False

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user)

    # ----- Scope results -----
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if is_owner(request.user) or is_admin(request.user):
            return qs
        if is_hr(request.user):
            return qs.filter(role=User.Roles.EMPLOYEE)
        if is_employee(request.user):
            # See self + all Clients
            return qs.filter(Q(pk=request.user.pk) | Q(role=User.Roles.CLIENT))
        return qs.none()

    # ----- Inlines shown per target user's role and viewer -----
    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        instances = []
        for inline_class in self.inlines:
            if inline_class is ClientProfileInline:
                # Show client profile inline only when viewing a Client,
                # and hide from HR (and optionally from Employees—keep or drop as you like)
                if obj.role == User.Roles.CLIENT and not is_hr(request.user):
                    instances.append(inline_class(self.model, self.admin_site))
            elif inline_class is EmployeeProfileInline:
                # Show employee profile inline when viewing company-side users
                if obj.role in (User.Roles.EMPLOYEE, User.Roles.ADMIN, User.Roles.OWNER):
                    instances.append(inline_class(self.model, self.admin_site))
        return instances

    # ----- Forms per viewer role -----
    def get_fieldsets(self, request, obj=None):
        base = list(super().get_fieldsets(request, obj))
        if is_owner(request.user):
            base.append((_('Role'), {"fields": ("role",)}))

        if is_admin(request.user) and not is_owner(request.user):
            return (
                (None, {"fields": ("username", "password")}),
                (_('Personal info'), {"fields": ("first_name", "last_name", "email")}),
                (_('Important dates'), {"fields": ("last_login", "date_joined")}),
            )

        if is_hr(request.user) and not is_owner(request.user):
            return (
                (None, {"fields": ("username", "password")}),
                (_('Personal info'), {"fields": ("first_name", "last_name", "email")}),
                (_('Important dates'), {"fields": ("last_login", "date_joined")}),
            )

        if is_employee(request.user) and not is_owner(request.user):
            # Minimal fields for employees; they can edit only their own record (enforced above)
            return (
                (None, {"fields": ("username", "password")}),
                (_('Personal info'), {"fields": ("first_name", "last_name", "email")}),
                (_('Important dates'), {"fields": ("last_login", "date_joined")}),
            )

        return tuple(base)

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "first_name", "last_name", "password1", "password2", "role"),
        }),
    )

    # ----- Read-only protections -----
    def get_readonly_fields(self, request, obj=None):
        ro = set(super().get_readonly_fields(request, obj))
        if not is_owner(request.user):
            ro.update({"is_superuser", "is_staff", "groups", "user_permissions", "last_login", "date_joined"})
        if is_admin(request.user) and not is_owner(request.user):
            ro.add("role")
        if is_hr(request.user) and not is_owner(request.user):
            ro.add("role")
        if is_employee(request.user) and not is_owner(request.user):
            # Employees never edit role/permissions; if viewing a Client, they have view-only anyway
            ro.add("role")
        return tuple(ro)

    # ----- Limit role choices (extra belt & suspenders) -----
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "role":
            if is_admin(request.user) and not is_owner(request.user):
                kwargs["choices"] = [(User.Roles.EMPLOYEE, "Employee"), (User.Roles.CLIENT, "Client")]
            if is_hr(request.user) and not is_owner(request.user):
                kwargs["choices"] = [(User.Roles.EMPLOYEE, "Employee")]
            if is_employee(request.user) and not is_owner(request.user):
                # Employees should never change role
                kwargs["choices"] = [(User.Roles.EMPLOYEE, "Employee")]  # not used when viewing Clients
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    # ----- Hide groups for non-Owners -----
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not is_owner(request.user) and "groups" in form.base_fields:
            form.base_fields["groups"].queryset = Group.objects.exclude(name__in=["Owner", "Admin"])
        return form

    # ----- Enforce policies on save -----
    def save_model(self, request, obj, form, change):
        # HR can only ever save users as EMPLOYEE
        if is_hr(request.user) and not is_owner(request.user):
            obj.role = User.Roles.EMPLOYEE

        # Admin cannot escalate to Admin/Owner
        if is_admin(request.user) and not is_owner(request.user):
            if obj.role in (User.Roles.ADMIN, User.Roles.OWNER):
                if change:
                    prev = type(obj).objects.get(pk=obj.pk)
                    obj.role = prev.role
                else:
                    obj.role = User.Roles.EMPLOYEE

        # Employees can only edit themselves (guarded above); keep role unchanged
        if is_employee(request.user) and not is_owner(request.user):
            if change and obj.pk != request.user.pk:
                # Shouldn't happen due to has_change_permission, but double-guard
                return
            # Never allow employee to change role
            if "role" in form.fields:
                obj.role = type(obj).objects.get(pk=obj.pk).role if change else User.Roles.EMPLOYEE

        super().save_model(request, obj, form, change)


# Optional: keep separate menu entries
@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name", "phone", "city", "state_region", "updated_at")
    search_fields = ("user__username", "user__email", "company_name", "phone", "city", "state_region", "postal_code")
    autocomplete_fields = ["user"]
    list_filter = ("country",)
    def has_module_permission(self, request):
        # Hide from HR if desired; allow Employees to see client profiles only if you want
        if is_hr(request.user):
            return False
        return super().has_module_permission(request)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "job_title", "work_phone", "discord_handle", "updated_at")
    search_fields = ("user__username", "user__email", "job_title", "work_phone", "slack_handle")
    autocomplete_fields = ["user"]
    list_filter = ("city", "state_region", "country")
    def has_module_permission(self, request):
        if is_hr(request.user):
            return True
        return super().has_module_permission(request)
