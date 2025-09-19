# ticketApp/admin.py
from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django.db.models import Count
from .models import Ticket, TicketMessage, TicketAttachment, TicketEvent

# ---------- permission helpers ----------
def is_owner(u):
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):
    return u.is_active and u.groups.filter(name="HR").exists()

def can_edit(u):
    return is_owner(u) or is_admin(u)


# ============================ Inlines ============================

class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    fields = ("file", "original_name", "uploaded_at")
    readonly_fields = ("uploaded_at",)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class TicketMessageInline(admin.StackedInline):
    model = TicketMessage
    extra = 0
    fields = ("author", "author_kind", "is_internal", "body", "created_at")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("author",)
    show_change_link = True

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class TicketEventInline(admin.TabularInline):
    model = TicketEvent
    extra = 0
    can_delete = False
    fields = ("kind", "at", "actor", "data")
    readonly_fields = ("kind", "at", "actor", "data")
    show_change_link = False


# ============================ ModelAdmins ============================

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display  = (
        "public_key", "subject", "company", "project",
        "status", "priority", "assigned_to", "customer_user",
        "updated_at", "last_client_reply_at",
        "attachments_link",  # ← new column with link
        "attention_flag",
    )
    list_filter   = ("status", "priority", "category")
    search_fields = ("public_key", "subject", "description", "company__name", "project__name", "assigned_to__username", "customer_user__username")
    autocomplete_fields = ("company", "project", "customer_user", "created_by", "assigned_to", "watchers")

    # IMPORTANT: remove TicketAttachmentInline here (no FK to Ticket)
    inlines = [TicketMessageInline, TicketEventInline]

    readonly_fields = ("public_key", "created_at", "updated_at", "last_client_reply_at")

    fieldsets = (
        ("Ticket", {"fields": ("company", "project", "public_key", "subject", "description", "category")}),
        ("Status", {"fields": ("status", "priority", "assigned_to")}),
        ("Client & Audit", {"fields": ("customer_user", "created_by", "watchers", "last_client_reply_at", "created_at", "updated_at")}),
    )

    actions = [
        "set_open", "set_inprogress", "set_pending_client", "set_resolved", "set_closed",
        "assign_to_me",
    ]

    # annotate attachment count for list display
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_attach_count=Count("messages__attachments"))

    def attachments_link(self, obj):
        count = getattr(obj, "_attach_count", 0) or 0
        url = (
            reverse("admin:ticketApp_ticketattachment_changelist")
            + "?"
            + urlencode({"message__ticket__id__exact": obj.id})
        )
        return format_html('<a href="{}">{}</a>', url, f"{count} file(s)")
    attachments_link.short_description = "Attachments"

    # simple visual cue: urgent open tickets
    def attention_flag(self, obj):
        if obj.status in (Ticket.Status.NEW, Ticket.Status.OPEN, Ticket.Status.INPROGRESS) and \
           obj.priority in (Ticket.Priority.HIGH, Ticket.Priority.URGENT):
            return format_html('<span style="color:#b91c1c;font-weight:600;">ATTN</span>')
        return ""
    attention_flag.short_description = ""

    # permissions (as before)
    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)

    # actions (unchanged)
    def set_open(self, request, queryset):
        updated = queryset.update(status=Ticket.Status.OPEN)
        self.message_user(request, f"Marked {updated} ticket(s) OPEN.")
    set_open.short_description = "Mark OPEN"

    def set_inprogress(self, request, queryset):
        updated = queryset.update(status=Ticket.Status.INPROGRESS)
        self.message_user(request, f"Marked {updated} ticket(s) IN PROGRESS.")
    set_inprogress.short_description = "Mark IN PROGRESS"

    def set_pending_client(self, request, queryset):
        updated = queryset.update(status=Ticket.Status.PENDING)
        self.message_user(request, f"Marked {updated} ticket(s) PENDING CLIENT.")
    set_pending_client.short_description = "Mark PENDING CLIENT"

    def set_resolved(self, request, queryset):
        now = timezone.now()
        updated = 0
        for t in queryset:
            t.status = Ticket.Status.RESOLVED
            t.closed_at = now
            t.save(update_fields=["status", "closed_at", "updated_at"])
            updated += 1
        self.message_user(request, f"Marked {updated} ticket(s) RESOLVED.")
    set_resolved.short_description = "Mark RESOLVED"

    def set_closed(self, request, queryset):
        now = timezone.now()
        updated = 0
        for t in queryset:
            t.status = Ticket.Status.CLOSED
            t.closed_at = now
            t.save(update_fields=["status", "closed_at", "updated_at"])
            updated += 1
        self.message_user(request, f"Closed {updated} ticket(s).")
    set_closed.short_description = "Mark CLOSED"

    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f"Assigned {updated} ticket(s) to you.")
    assign_to_me.short_description = "Assign to me"


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display  = ("ticket", "author", "author_kind", "is_internal", "created_at")
    list_filter   = ("author_kind", "is_internal")
    search_fields = ("ticket__public_key", "ticket__subject", "body")
    autocomplete_fields = ("ticket", "author")
    readonly_fields = ("created_at",)
    inlines = [TicketAttachmentInline]   # ← attachments live here

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)



@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display  = ("message", "original_name", "uploaded_at")
    search_fields = ("message__ticket__public_key", "original_name")
    autocomplete_fields = ("message",)
    readonly_fields = ("uploaded_at",)

    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    def has_add_permission(self, request): return can_edit(request.user)
    def has_change_permission(self, request, obj=None): return can_edit(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
