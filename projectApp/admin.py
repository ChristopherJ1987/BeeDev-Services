# projectApp/admin.py
from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from companyApp.models import CompanyMembership
from .models import (
    Project, ProjectMember, ProjectMilestone, ProjectEnvironment,
    ProjectLink, ProjectUpdate, ProjectUpdateAttachment, ProjectViewer
)

# -------- permission helpers (match your existing pattern) --------
def is_owner(u):
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):
    return u.is_active and u.groups.filter(name="HR").exists()

def is_plain_staff(u):
    return u.is_active and u.is_staff and not is_owner(u) and not is_admin(u) and not is_hr(u)


# =========================
# Inlines for Project page
# =========================
class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0
    autocomplete_fields = ("user",)
    fields = ("user", "role", "is_active", "added_at")
    readonly_fields = ("added_at",)

    # Limit selectable users to (staff OR members of the project's company)
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user":
            proj = getattr(request, "_current_project_obj", None)
            if proj and proj.pk:
                member_ids = CompanyMembership.objects.filter(
                    company=proj.company, is_active=True
                ).values_list("user_id", flat=True)
                field.queryset = field.queryset.filter(Q(is_staff=True) | Q(pk__in=member_ids))
        return field

class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0
    fields = ("sort_order", "name", "description", "state", "due_date", "completed_at", "is_client_visible")
    readonly_fields = ()

class ProjectEnvironmentInline(admin.TabularInline):
    model = ProjectEnvironment
    extra = 0
    fields = ("kind", "url", "health", "note", "last_checked_at", "last_updated_by")
    autocomplete_fields = ("last_updated_by",)

class ProjectLinkInline(admin.TabularInline):
    model = ProjectLink
    extra = 0
    fields = ("label", "url", "section", "visibility", "is_active", "sort_order", "notes")
    readonly_fields = ()

class ProjectViewerInline(admin.TabularInline):
    model = ProjectViewer
    extra = 0
    autocomplete_fields = ("user",)
    fields = ("user", "granted_by", "granted_at")
    readonly_fields = ("granted_at",)

    # Limit selectable users to members of the project's company
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user":
            proj = getattr(request, "_current_project_obj", None)
            if proj and proj.pk:
                member_ids = CompanyMembership.objects.filter(
                    company=proj.company, is_active=True
                ).values_list("user_id", flat=True)
                field.queryset = field.queryset.filter(pk__in=member_ids)
        return field

    # Auto-fill granted_by
    def save_new_instance(self, parent, form, commit=True):
        obj = super().save_new_instance(parent, form, commit=False)
        request = getattr(self, "request", None)
        if request and not obj.granted_by_id:
            obj.granted_by = request.user
        if commit:
            obj.save()
        return obj

    def get_formset(self, request, obj=None, **kwargs):
        self.request = request
        return super().get_formset(request, obj, **kwargs)


# =========================
# Project admin
# =========================
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [
        ProjectMemberInline,
        ProjectMilestoneInline,
        ProjectEnvironmentInline,
        ProjectLinkInline,
        ProjectViewerInline,
    ]

    list_display = (
        "name", "company", "status", "stage",
        "client_can_view_status", "client_can_view_links", "client_can_view_description",
        "percent_complete", "start_date", "target_launch_date", "actual_launch_date",
        "updated_at",
    )
    list_filter = (
        "company", "status", "stage",
        "client_can_view_status", "client_can_view_links", "client_can_view_description",
        "is_active",
    )
    search_fields = ("name", "company__name", "description", "scope_summary", "tags")
    ordering = ("company__name", "name")
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Identity", {"fields": ("company", "proposal", "name", "slug", "status", "stage", "is_active")}),
        ("Client Visibility", {"fields": ("client_can_view_status", "client_can_view_links", "client_can_view_description")}),
        ("Summary", {"fields": ("description", "scope_summary", "tags")}),
        ("Progress & Dates", {"fields": ("percent_complete", "start_date", "target_launch_date", "actual_launch_date")}),
        ("Ownership", {"fields": ("manager",)}),
        ("Audit", {"fields": ("created_by", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("company", "proposal", "manager", "created_by")

    # Pass current object to inlines (for filtering user choices)
    def get_form(self, request, obj=None, **kwargs):
        request._current_project_obj = obj
        return super().get_form(request, obj, **kwargs)

    # Permissions (block HR here; Owner/Admin can manage)
    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)
    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# =========================
# ProjectUpdate admin (with attachments)
# =========================
class ProjectUpdateAttachmentInline(admin.TabularInline):
    model = ProjectUpdateAttachment
    extra = 0
    fields = ("file", "original_name", "uploaded_at")
    readonly_fields = ("uploaded_at",)

@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    inlines = [ProjectUpdateAttachmentInline]

    list_display = ("project", "title", "visibility", "percent_complete_snapshot", "pinned", "posted_at")
    list_filter  = ("visibility", "pinned", "project__company")
    search_fields = ("project__name", "project__company__name", "title", "body")
    autocomplete_fields = ("project", "created_by")

    fields = (
        "project", "title", "body", "visibility",
        "percent_complete_snapshot", "pinned",
        "created_by", "posted_at",
    )
    readonly_fields = ("posted_at",)

    def has_module_permission(self, request):
        # Allow staff access; keep clients/HR out of admin for updates
        return request.user.is_staff
    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)
