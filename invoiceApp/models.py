# invoiceApp/models.py
import os, uuid, datetime, secrets
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# ---------- Validators / helpers ----------
PDF_VALIDATOR = FileExtensionValidator(["pdf"])
MAX_PDF_BYTES = 15 * 1024 * 1024

def _validate_size(file, max_bytes, label="file"):
    if file and file.size and file.size > max_bytes:
        raise ValidationError(f"{label} too large (> {max_bytes//1024//1024}MB).")

def invoice_pdf_upload_to(instance, filename):
    # MEDIA: invoices/<company>/<YYYY/MM>/<invoice-no or id>-<uuid>.pdf
    today = datetime.date.today()
    comp_bucket = getattr(getattr(instance, "company", None), "slug", None) or "company"
    ident = instance.number or f"inv-{instance.pk or 'new'}"
    return f"invoices/{comp_bucket}/{today.year}/{today.month:02d}/{ident}-{uuid.uuid4().hex}.pdf"


# =======================================================================
#                              INVOICE
# =======================================================================
class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT    = "DRAFT",    "Draft"
        SENT     = "SENT",     "Sent"
        PARTIAL  = "PARTIAL",  "Partially Paid"
        PAID     = "PAID",     "Paid"
        VOID     = "VOID",     "Void"

    company         = models.ForeignKey("companyApp.Company", on_delete=models.CASCADE, related_name="invoices")
    proposal        = models.ForeignKey("proposalApp.Proposal", null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices")

    # >>> NEW: Tie invoice to the client user (post-signup)
    customer_user   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="customer_invoices")
    # Optional: keep reference to the contact row used pre-signup
    customer_contact = models.ForeignKey("companyApp.CompanyContact", null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices")

    number      = models.CharField(max_length=40, unique=True, blank=True)  # generate on save if blank
    currency    = models.CharField(max_length=8, default="USD")
    issue_date  = models.DateField(default=datetime.date.today)
    due_date    = models.DateField(null=True, blank=True)

    # amounts
    subtotal       = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_total      = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total          = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # minimum due (deposit snapshot from proposal)
    minimum_due    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    amount_paid    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status         = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)

    # optional client access token (for a public invoice view)
    view_token     = models.CharField(max_length=64, unique=True, blank=True)

    # file
    pdf            = models.FileField(upload_to=invoice_pdf_upload_to, blank=True, null=True, validators=[PDF_VALIDATOR])
    created_by     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices_created")
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="InvoiceViewer",
        related_name="invoices_shared_with",
        blank=True,
    )

    def __str__(self):
        return f"Invoice {self.number} — {self.company.name}"

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["number"]),
            models.Index(fields=["company", "customer_user"]),  # >>> helpful for client portals
        ]

    def __str__(self):
        return self.number or f"Invoice #{self.pk}"

    # ---- derived amounts ----
    @property
    def balance_due(self) -> Decimal:
        return (self.total or Decimal("0.00")) - (self.amount_paid or Decimal("0.00"))

    def recalc_totals(self, *, save=True):
        sub = sum((li.subtotal or Decimal("0.00")) for li in self.line_items.all())
        disc = sum((ad.amount_applied or Decimal("0.00")) for ad in self.applied_discounts.all())
        self.subtotal = sub
        self.discount_total = disc
        base = (self.subtotal - self.discount_total).quantize(Decimal("0.01"))
        self.total = base + (self.tax_total or Decimal("0.00"))
        if save:
            self.save(update_fields=["subtotal", "discount_total", "total", "updated_at"])
        return self.total

    def refresh_status_from_payments(self, *, save=True):
        paid = sum((p.amount or Decimal("0.00")) for p in self.payments.all())
        self.amount_paid = paid
        new_status = self.Status.DRAFT if self.status == self.Status.DRAFT else (
            self.Status.PAID if self.balance_due <= Decimal("0.00")
            else self.Status.PARTIAL if paid > Decimal("0.00")
            else self.Status.SENT
        )
        self.status = new_status
        if save:
            self.save(update_fields=["amount_paid", "status", "updated_at"])

    def save(self, *args, **kwargs):
        if not self.view_token:
            self.view_token = secrets.token_urlsafe(32)
        if not self.number:
            base = timezone.now().strftime("%Y%m%d")
            self.number = f"INV-{base}-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    # --------- factory: create invoice from a signed proposal ---------
    @classmethod
    def from_proposal(cls, proposal, *, created_by=None, due_date=None, customer_user=None):
        """
        Build an invoice including:
        - All proposal line items
        - Snapshot of applied discounts
        - minimum_due from proposal.deposit_amount
        - Link to the client user (prefer explicit customer_user, otherwise proposal.contact.user)
        """
        # Prefer explicit user; else try proposal.contact.user; else leave null (can backfill later).
        if customer_user is None and getattr(proposal, "contact", None):
            customer_user = getattr(proposal.contact, "user", None)

        inv = cls.objects.create(
            company=proposal.company,
            proposal=proposal,
            customer_user=customer_user,
            customer_contact=getattr(proposal, "contact", None),
            currency=proposal.currency,
            due_date=due_date,
            minimum_due=proposal.deposit_amount or Decimal("0.00"),
            tax_total=proposal.amount_tax or Decimal("0.00"),
            created_by=created_by,
            status=cls.Status.SENT,  # commonly sent immediately after signing
        )
        # copy line items
        for li in proposal.line_items.all().order_by("sort_order", "pk"):
            InvoiceLineItem.objects.create(
                invoice=inv,
                sort_order=li.sort_order,
                name=li.name,
                description=li.description,
                quantity=li.quantity,
                unit_price=li.unit_price,
                subtotal=li.subtotal,
            )
        # copy discounts
        for ad in proposal.applied_discounts.all().order_by("sort_order", "id"):
            InvoiceAppliedDiscount.objects.create(
                invoice=inv,
                discount_code=ad.discount_code,
                name=ad.name,
                kind=ad.kind,
                value=ad.value,
                amount_applied=ad.amount_applied,
                sort_order=ad.sort_order,
            )
        inv.recalc_totals(save=True)
        return inv

# =======================================================================
#                          INVOICE LINE ITEMS
# =======================================================================
class InvoiceLineItem(models.Model):
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="line_items")
    sort_order  = models.PositiveIntegerField(default=0)
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity    = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    unit_price  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return f"{self.name} ({self.quantity} @ {self.unit_price})"

# =======================================================================
#                          INVOICE DISCOUNT
# =======================================================================
class InvoiceAppliedDiscount(models.Model):
    invoice       = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="applied_discounts")
    discount_code = models.SlugField(max_length=40)
    name          = models.CharField(max_length=120)
    kind          = models.CharField(max_length=10, choices=[("PERCENT","Percent"),("FIXED","Fixed amount")])
    value         = models.DecimalField(max_digits=10, decimal_places=2)
    amount_applied= models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    sort_order    = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")

# =======================================================================
#                             PAYMENT
# =======================================================================
class Payment(models.Model):
    class Method(models.TextChoices):
        CARD  = "CARD",  "Card"
        ACH   = "ACH",   "ACH / Bank"
        CHECK = "CHECK", "Check"
        CASH  = "CASH",  "Cash"
        OTHER = "OTHER", "Other"

    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    method      = models.CharField(max_length=10, choices=Method.choices, default=Method.CARD)
    reference   = models.CharField(max_length=120, blank=True)  # gateway id, check no, etc.

    # >>> NEW: who paid (client user), if known
    payer_user  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments_made")

    received_at = models.DateTimeField(default=timezone.now)
    notes       = models.TextField(blank=True)
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments_recorded")

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-received_at", "id")

    def __str__(self):
        return f"Payment {self.amount} on {self.invoice}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # After saving a payment, refresh invoice totals/status
        self.invoice.refresh_status_from_payments(save=True)

class InvoiceViewer(models.Model):
    """
    Per-invoice override: allow specific users (who belong to the invoice's company)
    to view this invoice even if their membership flags are off.
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="allowed_viewers")
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="allowed_invoices")

    class Meta:
        unique_together = [("invoice", "user")]
        indexes = [models.Index(fields=["invoice", "user"])]

    def __str__(self):
        return f"{self.user} can view {self.invoice}"