# projectApp/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    Project, ProjectMember, ProjectMilestone, ProjectUpdate, ProjectUpdateAttachment,
    ProjectEnvironment, ProjectLink
)

# ---------- permission helpers (same pattern as other apps) ----------
def is_owner(u):
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):
    return u.is_active and u.groups.filter(name="HR").exists()

def can_edit(u):
    return is_owner(u) or is_admin(u) or is_hr(u)


# ============================ Inlines ============================

class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0
    autocomplete_fields = ("user",)
    fields = ("user", "role", "is_active", "added_at")
    readonly_fields = ("added_at",)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 0
    fields = ("name", "state", "due_date", "completed_at", "is_client_visible", "sort_order", "description")
    readonly_fields = ()
    ordering = ("sort_order", "due_date")

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class ProjectEnvironmentInline(admin.TabularInline):
    model = ProjectEnvironment
    extra = 0
    fields = ("kind", "url", "health", "note", "last_checked_at", "last_updated_by")
    readonly_fields = ("last_checked_at",)
    autocomplete_fields = ("last_updated_by",)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class ProjectLinkInline(admin.TabularInline):
    model = ProjectLink
    extra = 0
    fields = ("label", "url", "section", "visibility", "is_active", "sort_order", "notes")
    readonly_fields = ()
    ordering = ("sort_order", "label")

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class ProjectUpdateAttachmentInline(admin.TabularInline):
    model = ProjectUpdateAttachment
    extra = 0
    fields = ("file", "original_name", "uploaded_at")
    readonly_fields = ("uploaded_at",)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class ProjectUpdateInline(admin.StackedInline):
    model = ProjectUpdate
    extra = 0
    fields = (
        "title", "body", "visibility", "percent_complete_snapshot",
        "pinned", "created_by", "posted_at"
    )
    readonly_fields = ("posted_at",)
    autocomplete_fields = ("created_by",)
    show_change_link = True
    inlines = [ProjectUpdateAttachmentInline]  # NOTE: nested inlines are not supported by Django admin.
                                               # Attachments will be edited on the update detail page.

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


# ============================ ModelAdmins ============================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display  = (
        "name", "company", "manager", "status", "stage",
        "percent_complete", "target_launch_date", "is_active", "updated_at",
    )
    list_filter   = ("status", "stage", "is_active")
    search_fields = ("name", "company__name", "slug", "manager__username", "manager__email")
    autocomplete_fields = ("company", "proposal", "manager", "created_by")
    inlines = [ProjectMemberInline, ProjectMilestoneInline, ProjectEnvironmentInline, ProjectLinkInline]
    readonly_fields = ("slug", "created_at", "updated_at")

    fieldsets = (
        ("Project", {"fields": ("company", "proposal", "name", "slug", "description", "scope_summary")}),
        ("Status", {"fields": ("status", "stage", "percent_complete", "is_active")}),
        ("Dates", {"fields": ("start_date", "target_launch_date", "actual_launch_date")}),
        ("Ownership", {"fields": ("manager", "tags", "created_by", "created_at", "updated_at")}),
    )

    actions = ["mark_active", "mark_complete", "set_stage_build", "pin_latest_update"]

    # permissions
    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return can_edit(request.user)
    def has_change_permission(self, request, obj=None): return can_edit(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)

    # actions
    def mark_active(self, request, queryset):
        updated = queryset.update(status=Project.Status.ACTIVE, is_active=True)
        self.message_user(request, f"Marked {updated} project(s) ACTIVE.")
    mark_active.short_description = "Mark selected projects as ACTIVE"

    def mark_complete(self, request, queryset):
        updated = queryset.update(status=Project.Status.COMPLETE, is_active=False, actual_launch_date=timezone.now().date())
        self.message_user(request, f"Marked {updated} project(s) COMPLETE.")
    mark_complete.short_description = "Mark selected projects as COMPLETE"

    def set_stage_build(self, request, queryset):
        updated = queryset.update(stage=Project.Stage.BUILD)
        self.message_user(request, f"Set stage=BUILD for {updated} project(s).")
    set_stage_build.short_description = "Set stage to BUILD"

    def pin_latest_update(self, request, queryset):
        count = 0
        for p in queryset:
            latest = p.updates.order_by("-posted_at").first()
            if latest:
                # unpin others
                p.updates.filter(pinned=True).update(pinned=False)
                latest.pinned = True
                latest.save(update_fields=["pinned"])
                count += 1
        self.message_user(request, f"Pinned latest update for {count} project(s).")
    pin_latest_update.short_description = "Pin latest update"


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display  = ("project", "title", "visibility", "percent_complete_snapshot", "pinned", "posted_at", "created_by")
    list_filter   = ("visibility", "pinned")
    search_fields = ("project__name", "title", "body")
    autocomplete_fields = ("project", "created_by")
    inlines = [ProjectUpdateAttachmentInline]
    readonly_fields = ("posted_at",)

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return can_edit(request.user)
    def has_change_permission(self, request, obj=None): return can_edit(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
