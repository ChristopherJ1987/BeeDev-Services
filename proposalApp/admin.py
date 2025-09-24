# proposalApp/admin.py
from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from companyApp.models import CompanyMembership
from userApp.models import User
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
    ProposalViewer,
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

    def has_view_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)


@admin.register(BaseSetting)
class BaseSettingAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "base_rate", "is_active", "sort_order")
    list_filter  = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("sort_order", "name")

    def has_view_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "kind", "value", "is_active")
    list_filter  = ("is_active", "kind")
    search_fields = ("name", "code")
    ordering = ("code",)

    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    def has_view_permission(self, request, obj=None): return self.has_module_permission(request)
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display  = ("name", "code", "job_rate", "base_setting", "default_hours", "default_quantity", "is_active", "sort_order")
    list_filter   = ("is_active", "job_rate", "base_setting")
    search_fields = ("name", "code", "tags")
    ordering      = ("sort_order", "name")
    autocomplete_fields = ("job_rate", "base_setting")

    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    def has_view_permission(self, request, obj=None): return self.has_module_permission(request)
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)


@admin.register(CostTier)
class CostTierAdmin(admin.ModelAdmin):
    list_display  = ("label", "code", "min_total", "max_total", "is_active", "sort_order")
    list_filter   = ("is_active",)
    search_fields = ("label", "code", "notes")
    ordering      = ("sort_order", "min_total")

    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True
    def has_view_permission(self, request, obj=None): return self.has_module_permission(request)
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)


# ---------------------------
# Drafts
# ---------------------------

class DraftItemInline(admin.TabularInline):
    model = DraftItem
    extra = 0
    fields = (
        "sort_order",
        "catalog_item",
        "name", "description", "job_rate", "base_setting",
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
        "estimate_manual",
        "deposit_type", "deposit_value", "deposit_amount",
        "remaining_due",
        "approval_status", "approved_by", "approved_at",
        "created_at",
    )
    list_filter = ("company", "deposit_type", "approval_status", "created_at")
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
                "estimate_manual",
                "estimate_tier",
                ("estimate_low", "estimate_high"),
            ),
        }),
        ("Approval", {
            "fields": (
                "approval_status",
                ("submitted_at", "approved_at", "approved_by"),
                "approval_notes",
            ),
        }),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    readonly_fields = (
        "subtotal", "discount_amount", "total",
        "deposit_amount", "remaining_due",
        "estimate_low", "estimate_high",
        "created_at", "updated_at",
        "submitted_at", "approved_at", "approved_by",
    )

    actions = [
        "action_recalc_totals",
        "action_submit_for_approval",
        "action_approve_drafts",
        "action_reject_drafts",
        "action_convert_to_proposal",
    ]

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

    @admin.action(description="Submit for approval")
    def action_submit_for_approval(self, request, queryset):
        count = 0
        for d in queryset:
            if getattr(d, "approval_status", None) in (getattr(ProposalDraft.ApprovalStatus, "DRAFT", "DRAFT"),
                                                       getattr(ProposalDraft.ApprovalStatus, "REJECTED", "REJECTED")):
                d.mark_submitted(actor=request.user, save=True)
                count += 1
        self.message_user(request, f"Submitted {count} draft(s) for approval.", level=messages.SUCCESS)

    @admin.action(description="Approve selected (Owner/Admin only)")
    def action_approve_drafts(self, request, queryset):
        if not (is_owner(request.user) or is_admin(request.user)):
            self.message_user(request, "You do not have permission to approve drafts.", level=messages.ERROR)
            return
        count = 0
        for d in queryset:
            if getattr(d, "approval_status", None) in (getattr(ProposalDraft.ApprovalStatus, "SUBMITTED", "SUBMITTED"),
                                                       getattr(ProposalDraft.ApprovalStatus, "DRAFT", "DRAFT")):
                d.mark_approved(actor=request.user, save=True)
                count += 1
        self.message_user(request, f"Approved {count} draft(s).", level=messages.SUCCESS)

    @admin.action(description="Reject selected (Owner/Admin only)")
    def action_reject_drafts(self, request, queryset):
        if not (is_owner(request.user) or is_admin(request.user)):
            self.message_user(request, "You do not have permission to reject drafts.", level=messages.ERROR)
            return
        count = 0
        for d in queryset:
            if getattr(d, "approval_status", None) in (
                getattr(ProposalDraft.ApprovalStatus, "SUBMITTED", "SUBMITTED"),
                getattr(ProposalDraft.ApprovalStatus, "DRAFT", "DRAFT"),
                getattr(ProposalDraft.ApprovalStatus, "APPROVED", "APPROVED"),
            ):
                d.mark_rejected(actor=request.user, save=True)
                count += 1
        self.message_user(request, f"Rejected {count} draft(s).", level=messages.SUCCESS)

    @admin.action(description="Convert to Proposal")
    @transaction.atomic
    def action_convert_to_proposal(self, request, queryset):
        not_ok = queryset.exclude(approval_status=getattr(ProposalDraft.ApprovalStatus, "APPROVED", "APPROVED")).count()
        if not_ok:
            self.message_user(
                request,
                "Conversion blocked: All selected drafts must be APPROVED.",
                level=messages.ERROR,
            )
            return
        created = 0
        for draft in queryset:
            draft.recalc_totals(save=True)
            proposal = draft.convert_to_proposal(actor=request.user)
            try:
                if proposal and getattr(draft, "approved_by_id", None) and not getattr(proposal, "approver_user_id", None):
                    proposal.approver_user_id = draft.approved_by_id
                    proposal.save(update_fields=["approver_user"])
            except Exception:
                pass
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


class ProposalViewerInline(admin.TabularInline):
    model = ProposalViewer
    extra = 0
    autocomplete_fields = ("user",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user":
            prop = getattr(request, "_current_proposal_obj", None)
            if prop and prop.pk:
                member_user_ids = CompanyMembership.objects.filter(
                    company=prop.company, is_active=True
                ).values_list("user_id", flat=True)
                field.queryset = field.queryset.filter(pk__in=member_user_ids)
        return field


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    inlines = [
        ProposalRecipientInline,
        ProposalEventInline,
        ProposalLineItemInline,
        ProposalAppliedDiscountInline,
        ProposalViewerInline,
    ]

    list_display = (
        "title", "company", "currency",
        "amount_subtotal", "discount_total", "amount_tax", "amount_total",
        "deposit_type", "deposit_value", "deposit_amount",
        "remaining_due", "sent_at", "signed_at",
        "countersign_flag",
        "sign_link_short",
        "pdf_link",  # NEW column
        "created_at",
    )
    list_filter = ("company", "deposit_type", "countersign_required", "created_at")
    search_fields = ("title", "company__name")
    ordering = ("-created_at",)

    readonly_fields = (
        "created_at", "updated_at",
        "sent_at", "viewed_at", "signed_at",
        "sign_token", "token_expires_at",
        "sign_link_preview",
        "countersigned_at", "countersigned_by",
    )

    fieldsets = (
        ("Header", {"fields": ("company", "created_by", "title", "currency")}),
        ("Totals", {"fields": (("amount_subtotal", "discount_total", "amount_tax", "amount_total"),)}),
        ("Deposit", {"fields": (("deposit_type", "deposit_value", "deposit_amount"), "remaining_due")}),
        ("Signing", {"fields": ("sign_token", "token_expires_at", "sign_link_preview", "sent_at", "viewed_at", "signed_at")}),
        # NEW: PDF upload/replace
        ("Access / File", {"fields": ("pdf",)}),
        ("Approver / Countersign", {
            "fields": (
                "approver_user",
                "countersign_required",
                ("countersigned_at", "countersigned_by"),
                "countersign_notes",
            )
        }),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["action_generate_link", "action_mark_sent", "action_mark_signed", "action_mark_countersigned", "action_make_deposit_invoice", "action_create_project"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "approver_user" and field is not None:
            try:
                field.queryset = field.queryset.filter(role__in=[User.Roles.OWNER, User.Roles.ADMIN, User.Roles.EMPLOYEE])
            except Exception:
                pass
        return field

    def get_form(self, request, obj=None, **kwargs):
        request._current_proposal_obj = obj
        return super().get_form(request, obj, **kwargs)

    def countersign_flag(self, obj):
        if not obj.countersign_required:
            return "—"
        if obj.countersigned_at:
            return "✔︎"
        if obj.signed_at:
            return "⚠︎ due"
        return "…"
    countersign_flag.short_description = "Countersign"

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

    # NEW: quick PDF link in list
    def pdf_link(self, obj):
        try:
            if obj.pdf:
                return format_html('<a href="{}" target="_blank" rel="noopener">PDF</a>', obj.pdf.url)
        except Exception:
            pass
        return "—"
    pdf_link.short_description = "PDF"

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

    @admin.action(description="Mark countersigned")
    def action_mark_countersigned(self, request, queryset):
        n = 0
        for p in queryset:
            p.mark_countersigned(actor=request.user, save=True)
            n += 1
        self.message_user(request, f"Marked {n} proposal(s) as countersigned.", level=messages.SUCCESS)

    @admin.action(description="Create deposit invoice now")
    @transaction.atomic
    def action_make_deposit_invoice(self, request, queryset):
        created = 0
        for p in queryset:
            inv = p.create_deposit_invoice(actor=request.user)
            if inv is not None:
                created += 1
        self.message_user(request, f"Created {created} deposit invoice(s).", level=messages.SUCCESS)
    
    @admin.action(description="Create Project (from signed)")
    @transaction.atomic
    def action_create_project(self, request, queryset):
        created = 0
        skipped_unsigned = 0
        skipped_existing = 0

        for p in queryset:
            # Only allow creating a project once the client has signed
            if not getattr(p, "signed_at", None):
                skipped_unsigned += 1
                continue

            # Already has a project?
            if getattr(p, "projects", None) and p.projects.exists():
                skipped_existing += 1
                continue

            # Prefer approver or creator as manager; kickoff today = True
            proj = p.create_project(
                actor=request.user,
                kickoff_today=True,
                # manager defaults handled in create_project()
            )
            if proj:
                created += 1

        msg = f"Created {created} project(s)."
        if skipped_unsigned:
            msg += f" Skipped {skipped_unsigned} (not signed)."
        if skipped_existing:
            msg += f" Skipped {skipped_existing} (already had a project)."
        self.message_user(request, msg, level=messages.SUCCESS if created else messages.INFO)
