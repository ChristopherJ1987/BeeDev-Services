# invoiceApp/admin.py
from decimal import Decimal
from django.contrib import admin
from django.utils.html import format_html
from .models import Invoice, InvoiceLineItem, InvoiceAppliedDiscount, Payment

# ---- permission helpers (same pattern) ----
def is_owner(u):
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):
    return u.is_active and u.groups.filter(name="HR").exists()

def is_plain_staff(u):
    return u.is_active and u.is_staff and not (is_owner(u) or is_admin(u) or is_hr(u))


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 0
    fields = ("sort_order", "name", "description", "quantity", "unit_price", "subtotal")
    readonly_fields = ()


class InvoiceAppliedDiscountInline(admin.TabularInline):
    model = InvoiceAppliedDiscount
    extra = 0
    fields = ("discount_code", "name", "kind", "value", "amount_applied", "sort_order")
    readonly_fields = ()


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = (
        "amount", "method", "reference", "payer_user", "received_at", "notes", "created_by",
        # --- Stripe (read-only in inline to avoid clutter) ---
        "stripe_payment_intent_id", "stripe_charge_id", "stripe_payment_method_id", "stripe_receipt_url", "gateway_status",
    )
    autocomplete_fields = ("payer_user", "created_by")
    readonly_fields = ("stripe_payment_intent_id", "stripe_charge_id", "stripe_payment_method_id", "stripe_receipt_url", "gateway_status")

    def has_add_permission(self, request, obj):
        # HR can record payments? Keep consistent with your policy:
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "number", "company", "customer_user", "status",
        "total", "amount_paid", "balance_display",
        "due_date",
        # --- Stripe glance ---
        "stripe_status", "stripe_invoice_short", "stripe_pi_short",
        "updated_at",
    )
    list_filter  = ("status", "currency")
    search_fields = ("number", "company__name", "customer_user__username", "customer_user__email", "stripe_invoice_id", "stripe_payment_intent_id")
    autocomplete_fields = ("company", "proposal", "customer_user", "customer_contact", "created_by")
    inlines = [InvoiceLineItemInline, InvoiceAppliedDiscountInline, PaymentInline]

    fieldsets = (
        ("Header", {"fields": ("number", "company", "proposal", "customer_user", "customer_contact", "currency", "issue_date", "due_date", "status")}),
        ("Amounts", {"fields": ("subtotal", "discount_total", "tax_total", "total", "minimum_due", "amount_paid")}),
        ("Access / File", {"fields": ("view_token", "pdf")}),
        # --- Stripe pane ---
        ("Stripe", {
            "fields": (
                "stripe_status",
                ("stripe_customer_id", "stripe_invoice_id"),
                ("stripe_checkout_session_id", "stripe_payment_intent_id"),
                "stripe_hosted_invoice_url",
                "stripe_invoice_link",
            )
        }),
        ("Audit", {"fields": ("created_by", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "stripe_invoice_link")

    actions = ["recalc_totals_action", "refresh_status_action", "clear_stripe_refs_action"]

    def balance_display(self, obj):
        value = obj.balance_due or Decimal("0.00")
        return format_html("<b>{}</b>", f"{value:.2f}")
    balance_display.short_description = "Balance Due"

    # Quick link to hosted invoice if present
    def stripe_invoice_link(self, obj):
        url = getattr(obj, "stripe_hosted_invoice_url", "") or ""
        if url:
            return format_html('<a href="{}" target="_blank" rel="noopener">Open hosted invoice</a>', url)
        return "—"
    stripe_invoice_link.short_description = "Hosted Invoice"

    # Compact shorts for list_display
    def stripe_invoice_short(self, obj):
        sid = getattr(obj, "stripe_invoice_id", "") or ""
        return f"...{sid[-8:]}" if sid else "—"
    stripe_invoice_short.short_description = "Stripe Inv"

    def stripe_pi_short(self, obj):
        pid = getattr(obj, "stripe_payment_intent_id", "") or ""
        return f"...{pid[-8:]}" if pid else "—"
    stripe_pi_short.short_description = "PI"

    # Permissions
    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user):
            return True
        return False
    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Actions
    def recalc_totals_action(self, request, queryset):
        for inv in queryset:
            inv.recalc_totals(save=True)
        self.message_user(request, f"Recalculated totals for {queryset.count()} invoice(s).")
    recalc_totals_action.short_description = "Recalculate totals"

    def refresh_status_action(self, request, queryset):
        for inv in queryset:
            inv.refresh_status_from_payments(save=True)
        self.message_user(request, f"Refreshed status for {queryset.count()} invoice(s).")
    refresh_status_action.short_description = "Refresh status from payments"

    @admin.action(description="Clear Stripe refs (debug)")
    def clear_stripe_refs_action(self, request, queryset):
        updated = 0
        fields = [
            "stripe_customer_id", "stripe_invoice_id", "stripe_checkout_session_id",
            "stripe_payment_intent_id", "stripe_hosted_invoice_url", "stripe_status",
        ]
        for inv in queryset:
            dirty = False
            for f in fields:
                if getattr(inv, f, ""):
                    setattr(inv, f, "")
                    dirty = True
            if dirty:
                inv.save(update_fields=fields + ["updated_at"])
                updated += 1
        self.message_user(request, f"Cleared Stripe refs on {updated} invoice(s).")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "invoice", "amount", "method", "gateway_status",
        "payer_user", "received_at", "reference",
        # Stripe glance
        "stripe_pi_short", "stripe_charge_short",
    )
    list_filter  = ("method", "gateway_status")
    search_fields = (
        "invoice__number", "reference", "payer_user__username", "payer_user__email",
        "stripe_payment_intent_id", "stripe_charge_id"
    )
    autocomplete_fields = ("invoice", "payer_user", "created_by")
    readonly_fields = ("created_at", "updated_at")

    fields = (
        "invoice", "amount", "method", "reference",
        "payer_user", "received_at", "notes",
        "gateway_status",
        # Stripe block
        "stripe_payment_intent_id", "stripe_charge_id", "stripe_payment_method_id", "stripe_receipt_url",
        "gateway_payload",
        "created_by", "created_at", "updated_at",
    )

    # Compact shorts
    def stripe_pi_short(self, obj):
        pid = getattr(obj, "stripe_payment_intent_id", "") or ""
        return f"...{pid[-8:]}" if pid else "—"
    stripe_pi_short.short_description = "PI"

    def stripe_charge_short(self, obj):
        cid = getattr(obj, "stripe_charge_id", "") or ""
        return f"...{cid[-8:]}" if cid else "—"
    stripe_charge_short.short_description = "Charge"

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
