# proposalApp/admin.py
from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    JobRate,
    BaseSetting,
    Discount,
    CatalogItem,
    ProposalDraft,
    DraftItem,
    Proposal,
    ProposalLineItem,
    ProposalAppliedDiscount,
    ProposalRecipient,
    ProposalEvent,
    CostTier,
)

# -------- permission helpers --------
def is_owner(u):
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):
    return u.is_active and u.groups.filter(name="HR").exists()

def is_plain_staff(u):
    return u.is_active and u.is_staff and not is_owner(u) and not is_admin(u) and not is_hr(u)

# ---------------------------
# Reference/Admin catalogs
# ---------------------------

@admin.register(JobRate)
class JobRateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "hourly_rate", "is_active", "sort_order")
    list_filter  = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("sort_order", "name")

    # ----- permissions -----    
    def has_view_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


@admin.register(BaseSetting)
class BaseSettingAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "base_rate", "is_active", "sort_order")
    list_filter  = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("sort_order", "name")

    # ----- permissions -----
    def has_view_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "kind", "value", "is_active")
    list_filter  = ("is_active", "kind")
    search_fields = ("name", "code")
    ordering = ("code",)

    # ----- permissions -----
    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display  = ("name", "code", "job_rate", "base_setting", "default_hours", "default_quantity", "is_active", "sort_order")
    list_filter   = ("is_active", "job_rate", "base_setting")
    search_fields = ("name", "code", "tags")
    ordering      = ("sort_order", "name")
    autocomplete_fields = ("job_rate", "base_setting")

    # ----- permissions -----
    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

@admin.register(CostTier)
class CostTierAdmin(admin.ModelAdmin):
    list_display  = ("label", "code", "min_total", "max_total", "is_active", "sort_order")
    list_filter   = ("is_active",)
    search_fields = ("label", "code", "notes")
    ordering      = ("sort_order", "min_total")

    # ----- permissions -----
    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    
    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


# ---------------------------
# Drafts
# ---------------------------

class DraftItemInline(admin.TabularInline):
    """
    Staff picks a CatalogItem; name/desc/job_rate/base snapshot automatically.
    Only hours/quantity are edited; line_total is computed.
    """
    model = DraftItem
    extra = 0
    fields = (
        "sort_order",
        "catalog_item",    # dropdown picker
        "name", "description", "job_rate", "base_setting",  # readonly snapshots
        "hours", "quantity",
        "line_total",
    )
    readonly_fields = ("name", "description", "job_rate", "base_setting", "line_total")
    autocomplete_fields = ("catalog_item",)


@admin.register(ProposalDraft)
class ProposalDraftAdmin(admin.ModelAdmin):
    inlines = [DraftItemInline]

    list_display = (
        "title", "company", "currency",
        "subtotal", "discount", "discount_amount",
        "total",
        "estimate_tier", "estimate_low", "estimate_high",
        "estimate_manual",                      # NEW
        "deposit_type", "deposit_value", "deposit_amount",
        "remaining_due", "created_at",
    )
    list_filter = ("company", "deposit_type", "created_at")
    search_fields = ("title", "company__name", "contact_name", "contact_email")
    ordering = ("-created_at",)

    fieldsets = (
        ("Header", {"fields": ("company", "created_by", "title", "currency")}),
        ("Optional Contact", {"fields": ("contact_name", "contact_email"), "classes": ("collapse",)}),
        ("Discount", {"fields": ("discount", "discount_amount")}),
        ("Totals & Deposit", {
            "fields": (
                ("subtotal", "total"),
                ("deposit_type", "deposit_value", "deposit_amount"),
                "remaining_due",
            )
        }),
        ("Estimated Tier", {
            "fields": (
                "estimate_manual",             # NEW toggle
                "estimate_tier",
                ("estimate_low", "estimate_high"),
            ),
        }),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = (
        "subtotal", "discount_amount", "total",
        "deposit_amount", "remaining_due",
        "estimate_low", "estimate_high",
        "created_at", "updated_at",
    )

    actions = ["action_recalc_totals", "action_convert_to_proposal"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.recalc_totals(save=True)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalc_totals(save=True)

    @admin.action(description="Recalculate totals")
    def action_recalc_totals(self, request, queryset):
        for draft in queryset:
            draft.recalc_totals(save=True)
        self.message_user(request, f"Recalculated totals for {queryset.count()} draft(s).", level=messages.SUCCESS)

    @admin.action(description="Convert to Proposal")
    @transaction.atomic
    def action_convert_to_proposal(self, request, queryset):
        created = 0
        for draft in queryset:
            draft.recalc_totals(save=True)
            draft.convert_to_proposal(actor=request.user)
            created += 1
        self.message_user(request, f"Created {created} proposal(s) from selected draft(s).", level=messages.SUCCESS)


# ---------------------------
# Proposals
# ---------------------------

class ProposalRecipientInline(admin.TabularInline):
    model = ProposalRecipient
    extra = 0
    fields = ("is_primary", "name", "email", "delivered_at", "last_opened_at")


class ProposalEventInline(admin.TabularInline):
    model = ProposalEvent
    extra = 0
    can_delete = False
    readonly_fields = ("kind", "at", "actor", "ip_address", "data")
    fields = ("kind", "at", "actor", "ip_address", "data")
    show_change_link = False


class ProposalLineItemInline(admin.TabularInline):
    """
    Read-only snapshot of the items that were materialized from the draft.
    Includes invoice-compatible fields for your Invoice.from_proposal() flow.
    """
    model = ProposalLineItem
    extra = 0
    readonly_fields = ("line_total", "unit_price", "subtotal")
    fields = (
        "sort_order", "name", "description",
        "hours", "quantity", "job_rate", "base_setting",
        "line_total", "unit_price", "subtotal",
    )


class ProposalAppliedDiscountInline(admin.TabularInline):
    model = ProposalAppliedDiscount
    extra = 0
    fields = ("discount_code", "name", "kind", "value", "amount_applied", "sort_order")
    can_delete = False


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    inlines = [ProposalRecipientInline, ProposalEventInline, ProposalLineItemInline, ProposalAppliedDiscountInline]

    list_display = (
        "title", "company", "currency",
        "amount_subtotal", "discount_total", "amount_tax", "amount_total",
        "deposit_type", "deposit_value", "deposit_amount",
        "remaining_due", "sent_at", "signed_at", "sign_link_short", "created_at",
    )
    list_filter = ("company", "deposit_type", "created_at")
    search_fields = ("title", "company__name")
    ordering = ("-created_at",)

    readonly_fields = (
        "created_at", "updated_at",
        "sent_at", "viewed_at", "signed_at",
        "sign_token", "token_expires_at",
        "sign_link_preview",
    )

    fieldsets = (
        ("Header", {
            "fields": ("company", "created_by", "title", "currency")
        }),
        ("Totals", {
            "fields": (("amount_subtotal", "discount_total", "amount_tax", "amount_total"),)
        }),
        ("Deposit", {
            "fields": (("deposit_type", "deposit_value", "deposit_amount"), "remaining_due")
        }),
        ("Signing", {
            "fields": ("sign_token", "token_expires_at", "sign_link_preview", "sent_at", "viewed_at", "signed_at")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    actions = ["action_generate_link", "action_mark_sent", "action_mark_signed", "action_make_deposit_invoice"]

    # ---- nice UI bits ----
    def sign_link_preview(self, obj):
        if not obj.pk:
            return "-"
        url = obj.get_signing_url()
        if url and url.startswith("http"):
            return format_html('<a href="{}" target="_blank" rel="noopener">Open signing link</a>', url)
        return mark_safe(url or "-")
    sign_link_preview.short_description = "Signing URL"

    def sign_link_short(self, obj):
        if not obj.sign_token:
            return "-"
        return f"...{obj.sign_token[-8:]}"
    sign_link_short.short_description = "Sign token"

    # ---- actions ----
    @admin.action(description="Generate signing link")
    def action_generate_link(self, request, queryset):
        n = 0
        for p in queryset:
            p.ensure_signing_link()
            n += 1
        self.message_user(request, f"Generated links for {n} proposal(s).", level=messages.SUCCESS)

    @admin.action(description="Mark sent (emails via hook)")
    def action_mark_sent(self, request, queryset):
        n = 0
        for p in queryset:
            p.mark_sent(actor=request.user)
            n += 1
        self.message_user(request, f"Marked {n} proposal(s) as sent.", level=messages.SUCCESS)

    @admin.action(description="Mark signed (create deposit invoice)")
    @transaction.atomic
    def action_mark_signed(self, request, queryset):
        n = 0
        for p in queryset:
            p.mark_signed(actor=request.user)
            n += 1
        self.message_user(request, f"Marked {n} proposal(s) signed and created deposit invoice(s).", level=messages.SUCCESS)

    @admin.action(description="Create deposit invoice now")
    @transaction.atomic
    def action_make_deposit_invoice(self, request, queryset):
        created = 0
        for p in queryset:
            inv = p.create_deposit_invoice(actor=request.user)
            if inv is not None:
                created += 1
        self.message_user(request, f"Created {created} deposit invoice(s).", level=messages.SUCCESS)
