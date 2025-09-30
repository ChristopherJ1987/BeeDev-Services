# projectApp/admin.py
from django.contrib import admin
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter

from companyApp.models import CompanyMembership
from .models import (
    Project, ProjectMember, ProjectMilestone, ProjectEnvironment,
    ProjectLink, ProjectUpdate, ProjectUpdateAttachment, ProjectViewer,
    # Additions:
    ProjectTask,
)

# If you created ProjectWeekNote (optional), import it; if not, comment this line.
try:
    from .models import ProjectWeekNote
    HAS_WEEK_NOTE = True
except Exception:
    HAS_WEEK_NOTE = False


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
# Custom list filters
# =========================
def monday_of(dt):
    return dt - timezone.timedelta(days=dt.weekday())

class PlannedWeekFilter(SimpleListFilter):
    title = "Planned week"
    parameter_name = "planned_week_start"

    def lookups(self, request, model_admin):
        return (
            ("this", "This week"),
            ("next", "Next week"),
            ("prev", "Last week"),
            ("any", "Has a week set"),
            ("none", "No week set"),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        today = timezone.localdate()
        this_mon = monday_of(today)
        if val == "this":
            return queryset.filter(planned_week_start=this_mon)
        if val == "next":
            return queryset.filter(planned_week_start=this_mon + timezone.timedelta(days=7))
        if val == "prev":
            return queryset.filter(planned_week_start=this_mon - timezone.timedelta(days=7))
        if val == "any":
            return queryset.exclude(planned_week_start__isnull=True)
        if val == "none":
            return queryset.filter(planned_week_start__isnull=True)
        return queryset


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

    # Preserve your pattern of capturing request on get_formset
    def get_formset(self, request, obj=None, **kwargs):
        self.request = request
        return super().get_formset(request, obj, **kwargs)

# ---- NEW: inline tasks on Project ----
class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0
    fields = (
        "title", "status", "priority",
        "planned_week_start", "due_date",
        "percent_complete", "sort_order",
        "is_client_visible", "show_priority_to_client",
        "assignees",
        "created_by", "created_at", "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("assignees", "created_by")
    show_change_link = True
    ordering = ("planned_week_start", "priority", "sort_order", "due_date")

    def has_add_permission(self, request, obj):
        return is_owner(request.user) or is_admin(request.user) or is_plain_staff(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user) or is_plain_staff(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


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
        ProjectTaskInline,      # << added
        ProjectViewerInline,
    ]

    list_display = (
        "name", "company", "status", "stage",
        # priority surface
        "priority", "show_priority_to_client",
        "client_can_view_status", "client_can_view_links", "client_can_view_description",
        "percent_complete", "start_date", "target_launch_date", "actual_launch_date",
        "updated_at",
    )
    list_filter = (
        "company", "status", "stage",
        "is_active",
        # priority & visibility
        "priority", "show_priority_to_client",
        "client_can_view_status", "client_can_view_links", "client_can_view_description",
    )
    search_fields = ("name", "company__name", "description", "scope_summary", "tags")
    ordering = ("company__name", "name")
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Identity", {"fields": ("company", "proposal", "name", "slug", "status", "stage", "is_active")}),
        ("Priority", {"fields": ("priority", "show_priority_to_client")}),
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

    # Permissions (block HR; Owner/Admin/staff allowed per your pattern)
    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user) or is_plain_staff(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# =========================
# ProjectTask admin
# =========================
@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = (
        "project", "title", "status", "priority",
        "planned_week_start", "due_date",
        "is_client_visible", "show_priority_to_client",
        "percent_complete",
        "created_by", "updated_at",
    )
    list_filter = (
        "status",
        PlannedWeekFilter,
        "is_client_visible",
        "show_priority_to_client",
        "project__company",
    )
    search_fields = ("title", "description", "project__name", "project__slug", "project__company__name")
    autocomplete_fields = ("project", "assignees", "created_by")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("project", "planned_week_start", "priority", "sort_order", "due_date")

    fieldsets = (
        ("Identity", {"fields": ("project", "title", "description")}),
        ("Status & Priority", {"fields": ("status", "priority", "percent_complete", "sort_order")}),
        ("Scheduling", {"fields": ("planned_week_start", "due_date")}),
        ("Assignment", {"fields": ("assignees",)}),
        ("Client Visibility", {"fields": ("is_client_visible", "show_priority_to_client")}),
        ("Audit", {"fields": ("created_by", "created_at", "updated_at")}),
    )

    def has_module_permission(self, request):
        # Allow staff to view/manage tasks
        return request.user.is_staff

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user) or is_plain_staff(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user) or is_plain_staff(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


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


# =========================
# Optional: ProjectWeekNote admin
# =========================
if HAS_WEEK_NOTE:
    @admin.register(ProjectWeekNote)
    class ProjectWeekNoteAdmin(admin.ModelAdmin):
        list_display = ("project", "week_start", "visibility", "created_by", "created_at")
        list_filter  = ("visibility", "project__company")
        search_fields = ("project__name", "project__slug", "body")
        autocomplete_fields = ("project", "created_by")
        readonly_fields = ("created_at",)
        ordering = ("-week_start", "project")

        fieldsets = (
            ("Identity", {"fields": ("project", "week_start")}),
            ("Visibility", {"fields": ("visibility",)}),
            ("Content", {"fields": ("body",)}),
            ("Audit", {"fields": ("created_by", "created_at")}),
        )

        def has_module_permission(self, request):
            return request.user.is_staff

        def has_add_permission(self, request):
            return is_owner(request.user) or is_admin(request.user) or is_plain_staff(request.user)

        def has_change_permission(self, request, obj=None):
            return is_owner(request.user) or is_admin(request.user) or is_plain_staff(request.user)

        def has_delete_permission(self, request, obj=None):
            return is_owner(request.user) or is_admin(request.user)
