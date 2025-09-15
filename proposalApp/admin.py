# proposalApp/admin.py
from datetime import timedelta
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    PricingRole, RateCard, LaborRate,
    ServiceCatalogItem,
    ProposalDraft, DraftSelection, DraftDiscount,
    Discount,
    Proposal, ProposalLineItem, ProposalAppliedDiscount, ProposalRecipient, ProposalEvent,
)

# If you renamed the app, adjust this import path:
from invoiceApp.models import Invoice


# ---------------- Permissions (same pattern as other apps) ----------------
def is_owner(u):
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):
    return u.is_active and u.groups.filter(name="HR").exists()

def is_plain_staff(u):
    return u.is_active and u.is_staff and not (is_owner(u) or is_admin(u) or is_hr(u))


# ============================== Pricing / Catalog ==============================

class LaborRateInline(admin.TabularInline):
    model = LaborRate
    extra = 0
    fields = ("role", "hourly_rate", "is_active", "sort_order")
    autocomplete_fields = ("role",)
    ordering = ("sort_order", "role__code")

@admin.register(RateCard)
class RateCardAdmin(admin.ModelAdmin):
    list_display = ("name", "currency", "effective_from", "effective_to", "is_default")
    list_filter = ("currency", "is_default")
    search_fields = ("name",)
    inlines = [LaborRateInline]

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user)

@admin.register(PricingRole)
class PricingRoleAdmin(admin.ModelAdmin):
    list_display = ("label", "code", "is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("label", "code")

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user)

@admin.register(ServiceCatalogItem)
class ServiceCatalogItemAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "item_type", "default_role", "fixed_price", "is_active", "sort_order")
    list_filter = ("item_type", "is_active")
    search_fields = ("name", "code", "tags")
    autocomplete_fields = ("default_role",)

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user)


# ============================== Discounts ==============================

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "kind", "value", "is_active", "starts_at", "ends_at")
    list_filter = ("kind", "is_active")
    search_fields = ("name", "code", "notes")
    ordering = ("code",)

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user)


# ============================== Drafts (employee-only) ==============================

class DraftSelectionInline(admin.TabularInline):
    model = DraftSelection
    extra = 0
    autocomplete_fields = ("catalog_item", "role")
    fields = (
        "catalog_item", "display_name", "item_type",
        "role", "hours", "quantity", "unit_price", "extended_price",
        "sort_order", "notes_internal",
    )
    readonly_fields = ("extended_price",)

class DraftDiscountInline(admin.TabularInline):
    model = DraftDiscount
    extra = 0
    autocomplete_fields = ("discount",)
    fields = ("discount", "kind", "value", "amount_applied", "sort_order", "notes")
    readonly_fields = ("amount_applied",)

@admin.register(ProposalDraft)
class ProposalDraftAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "rate_card", "status", "currency", "total", "deposit_amount", "updated_at")
    list_filter = ("status", "currency", "rate_card")
    search_fields = ("title", "company__name", "contact_email")
    autocomplete_fields = ("company", "created_by", "rate_card")
    inlines = [DraftSelectionInline, DraftDiscountInline]
    readonly_fields = ("subtotal", "discount_total", "tax_amount", "total", "deposit_amount", "created_at", "updated_at")

    fieldsets = (
        ("Header", {"fields": ("title", "company", "rate_card", "currency", "status")}),
        ("Contact (optional)", {"fields": ("contact_name", "contact_email")}),
        ("Deposit", {"fields": ("deposit_type", "deposit_value", "deposit_amount")}),
        ("Totals", {"fields": ("subtotal", "discount_total", "tax_amount", "total")}),
        ("Misc", {"fields": ("questionnaire", "internal_notes", "created_by", "created_at", "updated_at")}),
    )

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user) or is_hr(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user) or is_hr(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================== Proposals (final docs) ==============================

class ProposalLineItemInline(admin.TabularInline):
    model = ProposalLineItem
    extra = 0
    fields = ("sort_order", "name", "description", "quantity", "unit_price", "subtotal")

class ProposalAppliedDiscountInline(admin.TabularInline):
    model = ProposalAppliedDiscount
    extra = 0
    fields = ("discount_code", "name", "kind", "value", "amount_applied", "sort_order")

class ProposalRecipientInline(admin.TabularInline):
    model = ProposalRecipient
    extra = 0
    fields = ("is_primary", "name", "email", "delivered_at", "last_opened_at")

class ProposalEventInline(admin.TabularInline):
    model = ProposalEvent
    extra = 0
    can_delete = False
    fields = ("kind", "at", "actor", "ip_address", "data")
    readonly_fields = ("kind", "at", "actor", "ip_address", "data")
    show_change_link = False

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("company", "title", "version", "status", "amount_total", "sent_at", "viewed_at", "signed_at")
    list_filter  = ("status", "currency")
    search_fields = ("title", "company__name", "signed_by_email", "signed_by_name")
    autocomplete_fields = ("company", "created_by", "contact")
    inlines = [ProposalLineItemInline, ProposalAppliedDiscountInline, ProposalRecipientInline, ProposalEventInline]

    fieldsets = (
        ("Header", {"fields": ("company", "title", "version", "status", "currency", "valid_until")}),
        ("Amounts", {"fields": ("amount_subtotal", "discount_total", "amount_tax", "amount_total")}),
        ("Deposit", {"fields": ("deposit_type", "deposit_value", "deposit_amount")}),
        ("Lifecycle", {"fields": ("sign_token", "token_expires_at", "sent_at", "viewed_at", "signed_at", "declined_at")}),
        ("Files", {"fields": ("pdf_unsigned", "pdf_signed")}),
        ("Signature", {"fields": ("signed_by_name", "signed_by_email", "signer_ip", "signature_text", "signature_image", "signature_payload")}),
        ("Notes", {"fields": ("customer_notes", "internal_notes")}),
        ("Audit", {"fields": ("created_by", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    actions = ["mark_as_sent", "create_invoices_from_signed"]

    # ---- Permissions
    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user) or is_hr(request.user)
    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user): return True
        if is_hr(request.user): return True
        return False
    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def get_readonly_fields(self, request, obj=None):
        ro = set(super().get_readonly_fields(request, obj))
        # After SIGNED, lock for non Owner/Admin (keeps history immutable)
        if obj and obj.status == obj.Status.SIGNED and not (is_owner(request.user) or is_admin(request.user)):
            ro.update({
                "company", "title", "version", "currency", "valid_until",
                "amount_subtotal", "discount_total", "amount_tax", "amount_total",
                "deposit_type", "deposit_value", "deposit_amount",
                "sign_token", "token_expires_at", "sent_at", "viewed_at", "signed_at", "declined_at",
                "signed_by_name", "signed_by_email", "signer_ip", "signature_text", "signature_image", "signature_payload",
                "customer_notes", "internal_notes",
                "created_by",
            })
        return tuple(ro)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # ---- Actions
    def mark_as_sent(self, request, queryset):
        count = 0
        for p in queryset:
            p.mark_sent(actor=request.user)
            count += 1
        self.message_user(request, f"Marked {count} proposal(s) as SENT.")
    mark_as_sent.short_description = "Mark selected proposals as SENT"

    def create_invoices_from_signed(self, request, queryset):
        """
        Create an Invoice for each SELECTED proposal that is SIGNED.
        Prefer proposal.contact.user; else match by signed_by_email.
        Skips if not SIGNED, already invoiced, or no client user found.
        due_date = today + 14 days (adjust as needed).
        """
        User = get_user_model()
        created = skipped_not_signed = skipped_existing = skipped_no_user = 0
        due_date = timezone.now().date() + timedelta(days=14)

        for p in queryset:
            if p.status != p.Status.SIGNED:
                skipped_not_signed += 1
                continue
            if p.invoices.exists():
                skipped_existing += 1
                continue

            customer_user = None
            if getattr(p, "contact", None) and getattr(p.contact, "user", None):
                customer_user = p.contact.user
            elif p.signed_by_email:
                customer_user = User.objects.filter(email__iexact=p.signed_by_email).first()

            if not customer_user:
                skipped_no_user += 1
                continue

            Invoice.from_proposal(
                p,
                created_by=request.user,
                due_date=due_date,
                customer_user=customer_user,
            )
            created += 1

        bits = []
        if created: bits.append(f"created {created}")
        if skipped_not_signed: bits.append(f"skipped {skipped_not_signed} not signed")
        if skipped_existing: bits.append(f"skipped {skipped_existing} already invoiced")
        if skipped_no_user: bits.append(f"skipped {skipped_no_user} no client user")
        messages.info(request, " | ".join(bits) if bits else "No invoices created.")
    create_invoices_from_signed.short_description = "Create invoices from selected SIGNED proposals"
