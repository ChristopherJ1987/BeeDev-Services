# invoiceApp/admin.py
from decimal import Decimal
from django.contrib import admin
from django.utils.html import format_html

from .models import Invoice, InvoiceLineItem, InvoiceAppliedDiscount, Payment, InvoiceViewer
from companyApp.models import CompanyMembership  # for filtering allowed users

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
    fields = ("amount", "method", "reference", "payer_user", "received_at", "notes", "created_by")
    autocomplete_fields = ("payer_user", "created_by")

    def has_add_permission(self, request, obj):     # HR can record payments
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class InvoiceViewerInline(admin.TabularInline):
    """
    Per-invoice visibility overrides. Only members of the invoice's company
    should be selectable in the 'user' dropdown.
    """
    model = InvoiceViewer
    extra = 0
    autocomplete_fields = ("user",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "user":
            inv = getattr(request, "_current_invoice_obj", None)
            if inv and inv.pk:
                member_user_ids = CompanyMembership.objects.filter(
                    company=inv.company, is_active=True
                ).values_list("user_id", flat=True)
                field.queryset = field.queryset.filter(pk__in=member_user_ids)
        return field


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "company", "customer_user", "status", "total", "amount_paid", "balance_display", "due_date", "updated_at")
    list_filter  = ("status", "currency")
    search_fields = ("number", "company__name", "customer_user__username", "customer_user__email")
    autocomplete_fields = ("company", "proposal", "customer_user", "customer_contact", "created_by")
    inlines = [InvoiceLineItemInline, InvoiceAppliedDiscountInline, PaymentInline, InvoiceViewerInline]

    fieldsets = (
        ("Header", {"fields": ("number", "company", "proposal", "customer_user", "customer_contact", "currency", "issue_date", "due_date", "status")}),
        ("Amounts", {"fields": ("subtotal", "discount_total", "tax_total", "total", "minimum_due", "amount_paid")}),
        ("Access / File", {"fields": ("view_token", "pdf")}),
        ("Audit", {"fields": ("created_by", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    actions = ["recalc_totals_action", "refresh_status_action"]

    def balance_display(self, obj):
        value = obj.balance_due or Decimal("0.00")
        return format_html("<b>{}</b>", f"{value:.2f}")
    balance_display.short_description = "Balance Due"

    # Permissions
    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None):
        if is_owner(request.user) or is_admin(request.user):
            return True
        return False
    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    # Make current object available to inlines for filtering choices
    def get_form(self, request, obj=None, **kwargs):
        request._current_invoice_obj = obj
        return super().get_form(request, obj, **kwargs)

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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "method", "payer_user", "received_at", "reference")
    list_filter  = ("method",)
    search_fields = ("invoice__number", "reference", "payer_user__username", "payer_user__email")
    autocomplete_fields = ("invoice", "payer_user", "created_by")

    def has_module_permission(self, request): return request.user.is_staff
    def has_add_permission(self, request): return is_owner(request.user) or is_admin(request.user)
    def has_change_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
    def has_delete_permission(self, request, obj=None): return is_owner(request.user) or is_admin(request.user)
