# proposalApp/models.py
import os, uuid, datetime, secrets
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


# ---------- File validators / helpers ----------
PDF_VALIDATOR = FileExtensionValidator(["pdf"])
SIGN_IMG_VALIDATOR = FileExtensionValidator(["png", "jpg", "jpeg", "webp"])

MAX_PDF_BYTES = 15 * 1024 * 1024  # 15 MB
MAX_SIG_BYTES = 3 * 1024 * 1024   # 3 MB

def _validate_size(file, max_bytes, label="file"):
    if file and file.size and file.size > max_bytes:
        raise ValidationError(f"{label} too large (> {max_bytes//1024//1024}MB).")

def _company_bucket(instance) -> str:
    """Prefer company.slug → company.name → company.pk → 'company'."""
    c = getattr(instance, "company", None) or getattr(getattr(instance, "draft", None), "company", None)
    if not c:
        return "company"
    return getattr(c, "slug", None) or slugify(getattr(c, "name", "") or "") or f"company-{getattr(c, 'pk', 'x')}"

def unsigned_upload_to(instance, filename):
    # MEDIA: proposals/<company>/<YYYY/MM>/unsigned/<uuid>.pdf
    today = datetime.date.today()
    base = _company_bucket(instance)
    return f"proposals/{base}/{today.year}/{today.month:02d}/unsigned/{uuid.uuid4().hex}.pdf"

def signed_upload_to(instance, filename):
    # MEDIA: proposals/<company>/<YYYY/MM>/signed/<proposal-id>-<uuid>.pdf
    today = datetime.date.today()
    base = _company_bucket(instance)
    pid = instance.pk or "new"
    return f"proposals/{base}/{today.year}/{today.month:02d}/signed/{pid}-{uuid.uuid4().hex}.pdf"

def signature_image_upload_to(instance, filename):
    # MEDIA: proposals/<company>/<YYYY/MM>/signatures/<proposal-id>-<uuid>.<ext>
    today = datetime.date.today()
    base = _company_bucket(instance)
    pid = instance.pk or "new"
    ext = os.path.splitext(filename)[1].lower()
    return f"proposals/{base}/{today.year}/{today.month:02d}/signatures/{pid}-{uuid.uuid4().hex}{ext}"


# =======================================================================
#                            PRICING LAYER
# =======================================================================

class Discount(models.Model):
    class Kind(models.TextChoices):
        PERCENT = "PERCENT", "Percent"
        FIXED   = "FIXED",   "Fixed amount"

    code        = models.SlugField(max_length=40, unique=True)   # e.g. 'new-client', 'spring-20'
    name        = models.CharField(max_length=120)
    kind        = models.CharField(max_length=10, choices=Kind.choices, default=Kind.PERCENT)
    value       = models.DecimalField(max_digits=10, decimal_places=2)  # percent (e.g. 10.00) or fixed amount
    is_active   = models.BooleanField(default=True)
    starts_at   = models.DateField(null=True, blank=True)
    ends_at     = models.DateField(null=True, blank=True)
    notes       = models.TextField(blank=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.name} ({self.code})"

class PricingRole(models.Model):
    """
    Canonical roles used when pricing hourly work (e.g., 'DESIGN', 'DEV', 'PM').
    Kept separate so ServiceCatalog and RateCard can both reference the same roles.
    """
    code        = models.SlugField(max_length=40, unique=True)  # 'design', 'dev', 'pm'
    label       = models.CharField(max_length=80)               # 'Designer', 'Developer', 'Project Manager'
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    sort_order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "code")

    def __str__(self):
        return f"{self.label} ({self.code})"

class RateCard(models.Model):
    """
    A set of hourly rates (by role) effective for a period.
    Drafts reference a rate card to snapshot unit prices.
    """
    name           = models.CharField(max_length=120, unique=True)
    currency       = models.CharField(max_length=8, default="USD")
    effective_from = models.DateField(null=True, blank=True)
    effective_to   = models.DateField(null=True, blank=True)
    is_default     = models.BooleanField(default=False)
    notes          = models.TextField(blank=True)

    class Meta:
        ordering = ("-effective_from", "name")

    def __str__(self):
        return f"{self.name} ({self.currency})"

class LaborRate(models.Model):
    """
    Hourly rate for a specific role within a rate card.
    """
    rate_card  = models.ForeignKey(RateCard, on_delete=models.CASCADE, related_name="rates")
    role       = models.ForeignKey(PricingRole, on_delete=models.PROTECT, related_name="rates")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)

    sort_order = models.PositiveIntegerField(default=0)
    is_active  = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "role__code")
        unique_together = (("rate_card", "role"),)

    def __str__(self):
        return f"{self.rate_card}: {self.role.code} @ {self.hourly_rate}"

class ServiceCatalogItem(models.Model):
    """
    Items your staff can pick from when building a draft: hourly, fixed, or recurring.
    Hourly items can suggest a default role (e.g., DEV).
    """
    class ItemType(models.TextChoices):
        HOURLY    = "HOURLY",    "Hourly"
        FIXED     = "FIXED",     "Fixed Fee"
        RECURRING = "RECURRING", "Recurring"

    class BillingPeriod(models.TextChoices):
        MONTHLY = "MONTHLY", "Monthly"
        YEARLY  = "YEARLY",  "Yearly"
        OTHER   = "OTHER",   "Other"

    code         = models.SlugField(max_length=60, unique=True)  # 'web-dev', 'design', 'seo-monthly'
    name         = models.CharField(max_length=160)
    description  = models.TextField(blank=True)
    item_type    = models.CharField(max_length=12, choices=ItemType.choices, default=ItemType.HOURLY)
    default_role = models.ForeignKey(PricingRole, null=True, blank=True, on_delete=models.SET_NULL)

    # Defaults used when adding to a draft (can be overridden at selection)
    default_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    fixed_price   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    period        = models.CharField(max_length=12, choices=BillingPeriod.choices, blank=True, default="")

    is_active   = models.BooleanField(default=True)
    sort_order  = models.PositiveIntegerField(default=0)
    tags        = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return f"{self.name} [{self.item_type}]"


# =======================================================================
#                          DRAFT (CHECKLIST) LAYER
# =======================================================================

class ProposalDraft(models.Model):
    """
    Employee-only working copy before a Proposal is generated.
    Snapshots unit prices from the chosen RateCard so drafts are stable.
    """
    class Status(models.TextChoices):
        DRAFT      = "DRAFT",      "Draft"
        READY      = "READY",      "Ready"
        CONVERTED  = "CONVERTED",  "Converted to Proposal"
        CANCELED   = "CANCELED",   "Canceled"

    class DepositType(models.TextChoices):
        NONE    = "NONE",    "None"
        PERCENT = "PERCENT", "Percent of total"
        FIXED   = "FIXED",   "Fixed amount"

    company     = models.ForeignKey("companyApp.Company", on_delete=models.CASCADE, related_name="proposal_drafts")
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="proposal_drafts")
    rate_card   = models.ForeignKey(RateCard, on_delete=models.PROTECT, related_name="drafts")
    title       = models.CharField(max_length=200)
    currency    = models.CharField(max_length=8, default="USD")

    # Optional: who it's addressed to (pre-account)
    contact_name  = models.CharField(max_length=160, blank=True)
    contact_email = models.EmailField(blank=True)

    # Optional: capture answers from your consultation checklist
    questionnaire = models.JSONField(blank=True, null=True)

    status      = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    internal_notes = models.TextField(blank=True)

    # totals
    subtotal    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total= models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_amount  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total       = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # deposit
    deposit_type  = models.CharField(max_length=10, choices=DepositType.choices, default=DepositType.NONE)
    deposit_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))  # percent or fixed
    deposit_amount= models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))  # computed snapshot

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Draft: {self.company.name} · {self.title}"

    def recalc_totals(self, *, save=True):
        items = list(self.selections.all())
        sub = sum((i.extended_price or Decimal("0.00")) for i in items)

        # discounts against subtotal
        disc_sum = Decimal("0.00")
        for dd in self.discounts.all().order_by("sort_order"):
            amt = dd.compute_amount(base_subtotal=sub) or Decimal("0.00")
            dd.amount_applied = amt
            dd.save(update_fields=["amount_applied"])
            disc_sum += amt

        self.subtotal       = sub
        self.discount_total = disc_sum

        base = (self.subtotal - self.discount_total).quantize(Decimal("0.01"))
        self.total = base + (self.tax_amount or Decimal("0.00"))

        # deposit snapshot
        if self.deposit_type == self.DepositType.PERCENT:
            self.deposit_amount = (self.total * (self.deposit_value or Decimal("0.00")) / Decimal("100.00")).quantize(Decimal("0.01"))
        elif self.deposit_type == self.DepositType.FIXED:
            self.deposit_amount = (self.deposit_value or Decimal("0.00")).quantize(Decimal("0.01"))
        else:
            self.deposit_amount = Decimal("0.00")

        if save:
            self.save(update_fields=["subtotal", "discount_total", "total", "deposit_amount", "updated_at"])
        return self.total

    def materialize_to_proposal(self, *, created_by=None, valid_until=None):
        """
        Create a Proposal and copy current selections as line items (snapshotted).
        Does NOT generate PDFs or send anything—views/services will handle that.
        """
        proposal = Proposal.objects.create(
            company=self.company,
            created_by=created_by,
            contact=None,
            title=self.title,
            version=1,
            status=Proposal.Status.DRAFT,
            currency=self.currency,
            amount_subtotal=self.subtotal,
            amount_tax=self.tax_amount,
            amount_total=self.total,
            valid_until=valid_until,
            customer_notes="",
            internal_notes=self.internal_notes,
            deposit_type=self.deposit_type,
            deposit_value=self.deposit_value,
            deposit_amount=self.deposit_amount,
            discount_total=self.discount_total,
        )
        # Copy selections to line items
        for sel in self.selections.all().order_by("sort_order", "pk"):
            ProposalLineItem.objects.create(
                proposal=proposal,
                sort_order=sel.sort_order,
                name=sel.display_name,
                description=sel.description,
                quantity=sel.quantity,
                unit_price=sel.unit_price,
                subtotal=sel.extended_price,
            )
        
        for dd in self.discounts.all().order_by("sort_order", "id"):
            ProposalAppliedDiscount.objects.create(
                proposal=proposal,
                discount_code=dd.discount.code,
                name=dd.discount.name,
                kind=dd.kind,
                value=dd.value,
                amount_applied=dd.amount_applied,
                sort_order=dd.sort_order,
            )

        self.status = self.Status.CONVERTED
        self.save(update_fields=["status", "updated_at"])
        ProposalEvent.objects.create(proposal=proposal, kind=ProposalEvent.Kind.CREATED, actor=created_by)
        return proposal
    
# -------------------- DRAFT DISCOUNTS (snapshot) --------------------
class DraftDiscount(models.Model):
    draft          = models.ForeignKey("ProposalDraft", on_delete=models.CASCADE, related_name="discounts")
    discount       = models.ForeignKey(Discount, on_delete=models.PROTECT, related_name="draft_usages")

    # Snapshot fields
    kind           = models.CharField(max_length=10, choices=Discount.Kind.choices)
    value          = models.DecimalField(max_digits=10, decimal_places=2)
    amount_applied = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    sort_order     = models.PositiveIntegerField(default=0)
    notes          = models.TextField(blank=True)

    class Meta:
        ordering = ("sort_order", "id")
        unique_together = (("draft", "discount"),)

    def __str__(self):
        return f"{self.draft} · {self.discount.code}"

    def compute_amount(self, *, base_subtotal: Decimal) -> Decimal:
        if self.kind == Discount.Kind.PERCENT:
            return (base_subtotal or Decimal("0.00")) * (self.value or Decimal("0.00")) / Decimal("100.00")
        return self.value or Decimal("0.00")

class DraftSelection(models.Model):
    """
    A selected catalog item in a draft, with snapshot pricing.
    """
    draft       = models.ForeignKey(ProposalDraft, on_delete=models.CASCADE, related_name="selections")
    catalog_item= models.ForeignKey(ServiceCatalogItem, on_delete=models.PROTECT, related_name="draft_selections")

    # Snapshot fields (so changes in catalog/rates won’t affect this draft)
    display_name = models.CharField(max_length=200)     # default=catalog_item.name (can override)
    description  = models.TextField(blank=True)
    item_type    = models.CharField(max_length=12, choices=ServiceCatalogItem.ItemType.choices)

    role         = models.ForeignKey(PricingRole, null=True, blank=True, on_delete=models.SET_NULL)  # for hourly
    hours        = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    quantity     = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))      # also for fixed/recurring
    unit_price   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))     # snapshotted from RateCard or fixed_price
    extended_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    notes_internal = models.TextField(blank=True)
    sort_order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return f"{self.display_name} ({self.item_type})"

    def save(self, *args, **kwargs):
        # On first save, prefill snapshot fields if not set
        if not self.pk:
            self.display_name = self.display_name or self.catalog_item.name
            self.description = self.description or self.catalog_item.description
            self.item_type = self.item_type or self.catalog_item.item_type
            if self.item_type == ServiceCatalogItem.ItemType.HOURLY:
                self.role = self.role or self.catalog_item.default_role
                # find rate from the draft's rate card
                unit = Decimal("0.00")
                if self.role:
                    lr = (self.draft.rate_card.rates.filter(role=self.role, is_active=True)
                          .order_by("sort_order").first())
                    if lr:
                        unit = lr.hourly_rate
                # extended = hours * unit * quantity
                self.unit_price = unit
                self.extended_price = (self.hours or Decimal("0.00")) * (self.unit_price or Decimal("0.00")) * (self.quantity or Decimal("1.00"))
            elif self.item_type == ServiceCatalogItem.ItemType.FIXED:
                self.unit_price = self.catalog_item.fixed_price
                self.extended_price = (self.unit_price or Decimal("0.00")) * (self.quantity or Decimal("1.00"))
            else:  # RECURRING
                # Treat initial proposal price as first period only (can customize later)
                self.unit_price = self.catalog_item.fixed_price
                self.extended_price = (self.unit_price or Decimal("0.00")) * (self.quantity or Decimal("1.00"))
        else:
            # Recompute extended price if edited
            if self.item_type == ServiceCatalogItem.ItemType.HOURLY:
                self.extended_price = (self.hours or Decimal("0.00")) * (self.unit_price or Decimal("0.00")) * (self.quantity or Decimal("1.00"))
            else:
                self.extended_price = (self.unit_price or Decimal("0.00")) * (self.quantity or Decimal("1.00"))
        super().save(*args, **kwargs)
        # Update draft totals (without recursion loops)
        self.draft.recalc_totals(save=True)


# =======================================================================
#                           PROPOSAL (FINAL)
# =======================================================================

class Proposal(models.Model):
    class Status(models.TextChoices):
        DRAFT    = "DRAFT",    "Draft"
        SENT     = "SENT",     "Sent"
        VIEWED   = "VIEWED",   "Viewed"
        SIGNED   = "SIGNED",   "Signed"
        DECLINED = "DECLINED", "Declined"
        EXPIRED  = "EXPIRED",  "Expired"
        CANCELED = "CANCELED", "Canceled"

    class DepositType(models.TextChoices):
        NONE    = "NONE",    "None"
        PERCENT = "PERCENT", "Percent of total"
        FIXED   = "FIXED",   "Fixed amount"

    company      = models.ForeignKey("companyApp.Company", on_delete=models.CASCADE, related_name="proposals")
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="proposals_created")
    contact      = models.ForeignKey("companyApp.CompanyContact", on_delete=models.SET_NULL, null=True, blank=True, related_name="proposals_for_contact")

    title        = models.CharField(max_length=200)
    version      = models.PositiveIntegerField(default=1)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    currency     = models.CharField(max_length=8, default="USD")

    amount_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_tax      = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_total    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    valid_until     = models.DateField(null=True, blank=True)

    deposit_type   = models.CharField(max_length=10, choices=DepositType.choices, default=DepositType.NONE)
    deposit_value  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))


    # Public signing link
    sign_token       = models.CharField(max_length=64, unique=True, editable=False)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Timeline stamps
    sent_at      = models.DateTimeField(null=True, blank=True)
    viewed_at    = models.DateTimeField(null=True, blank=True)
    signed_at    = models.DateTimeField(null=True, blank=True)
    declined_at  = models.DateTimeField(null=True, blank=True)

    # Files
    pdf_unsigned = models.FileField(upload_to=unsigned_upload_to, blank=True, null=True, validators=[PDF_VALIDATOR],
                                    help_text="Employee-only; retained for history.")
    pdf_signed   = models.FileField(upload_to=signed_upload_to,   blank=True, null=True, validators=[PDF_VALIDATOR],
                                    help_text="Client-visible after signing.")

    # Signature capture
    signed_by_name   = models.CharField(max_length=200, blank=True)
    signed_by_email  = models.EmailField(blank=True)
    signer_ip        = models.GenericIPAddressField(null=True, blank=True)
    signature_text   = models.CharField(max_length=200, blank=True)
    signature_image  = models.ImageField(upload_to=signature_image_upload_to, blank=True, null=True, validators=[SIGN_IMG_VALIDATOR])
    signature_payload = models.JSONField(blank=True, null=True)

    customer_notes   = models.TextField(blank=True)
    internal_notes   = models.TextField(blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["sign_token"]),
            models.Index(fields=["title"]),
        ]
        unique_together = (("company", "title", "version"),)

    def __str__(self):
        return f"{self.company.name} · {self.title} v{self.version}"

    @property
    def is_signed(self) -> bool:
        return self.status == self.Status.SIGNED and bool(self.signed_at)

    @property
    def client_can_view(self) -> bool:
        # Only the signed version is client-facing
        return self.is_signed and bool(self.pdf_signed)

    # --- model-level helpers (no views) ---
    def mark_sent(self, *, actor=None):
        if self.sent_at is None:
            self.sent_at = timezone.now()
        if self.status in {self.Status.DRAFT, self.Status.SENT}:
            self.status = self.Status.SENT
        self.save(update_fields=["sent_at", "status", "updated_at"])
        ProposalEvent.objects.create(proposal=self, kind=ProposalEvent.Kind.SENT, actor=actor)

    def mark_viewed(self, *, actor=None, ip=None, as_employee=False):
        first_time = False
        if not as_employee:
            if self.viewed_at is None:
                first_time = True
                self.viewed_at = timezone.now()
            if self.status in {self.Status.DRAFT, self.Status.SENT, self.Status.VIEWED}:
                self.status = self.Status.VIEWED
            self.save(update_fields=["viewed_at", "status", "updated_at"])
        ProposalEvent.objects.create(
            proposal=self, kind=ProposalEvent.Kind.VIEWED, actor=actor, ip_address=ip,
            data={"as_employee": as_employee, "first_time": first_time},
        )
        return first_time

    def clean(self):
        if self.pdf_unsigned:
            _validate_size(self.pdf_unsigned, MAX_PDF_BYTES, "unsigned PDF")
        if self.pdf_signed:
            _validate_size(self.pdf_signed, MAX_PDF_BYTES, "signed PDF")
        if self.signature_image:
            _validate_size(self.signature_image, MAX_SIG_BYTES, "signature image")
        if self.status == self.Status.SIGNED:
            if not self.pdf_signed:
                raise ValidationError("Signed proposals must include a signed PDF.")
            if not self.signed_by_name:
                raise ValidationError("Signed proposals must include 'signed_by_name'.")

    def save(self, *args, **kwargs):
        if not self.sign_token:
            self.sign_token = secrets.token_urlsafe(32)  # ~43 chars
        # If totals not set, compute from line items
        if (self.amount_subtotal or Decimal("0.00")) == Decimal("0.00") and self.pk:
            sub = sum((li.subtotal or Decimal("0.00")) for li in self.line_items.all())
            self.amount_subtotal = sub
            self.amount_total = sub + (self.amount_tax or Decimal("0.00"))
        super().save(*args, **kwargs)

# -------------------- PROPOSAL DISCOUNTS (snapshot) --------------------
class ProposalAppliedDiscount(models.Model):
    proposal       = models.ForeignKey("Proposal", on_delete=models.CASCADE, related_name="applied_discounts")
    discount_code  = models.SlugField(max_length=40)            # snapshot of Discount.code
    name           = models.CharField(max_length=120)           # snapshot of Discount.name
    kind           = models.CharField(max_length=10, choices=Discount.Kind.choices)
    value          = models.DecimalField(max_digits=10, decimal_places=2)  # percent or fixed amount
    amount_applied = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    sort_order     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")


class ProposalLineItem(models.Model):
    proposal    = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="line_items")
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


class ProposalRecipient(models.Model):
    """
    Who the proposal was (or will be) sent to.
    Supports multiple recipients and future per-recipient status if desired.
    """
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="recipients")
    name     = models.CharField(max_length=160, blank=True)
    email    = models.EmailField()
    is_primary = models.BooleanField(default=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    last_opened_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-is_primary", "email")
        unique_together = (("proposal", "email"),)

    def __str__(self):
        return f"{self.email} · {self.proposal}"


class ProposalEvent(models.Model):
    """
    Immutable audit trail of key events.
    """
    class Kind(models.TextChoices):
        CREATED    = "CREATED",    "Created"
        SENT       = "SENT",       "Sent"
        VIEWED     = "VIEWED",     "Viewed"
        SIGNED     = "SIGNED",     "Signed"
        DOWNLOADED = "DOWNLOADED", "Downloaded"
        COMMENT    = "COMMENT",    "Comment"
        UPDATED    = "UPDATED",    "Updated"
        DECLINED   = "DECLINED",   "Declined"

    proposal   = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="events")
    kind       = models.CharField(max_length=20, choices=Kind.choices)
    at         = models.DateTimeField(auto_now_add=True)
    actor      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="proposal_events")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    data       = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ("-at", "pk")

    def __str__(self):
        return f"{self.proposal} · {self.kind} @ {self.at:%Y-%m-%d %H:%M}"
