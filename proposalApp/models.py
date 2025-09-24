# proposalApp/models.py
from decimal import Decimal, ROUND_HALF_UP
import secrets
from importlib import import_module

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone


# ---------- Money helpers ----------
MONEY = Decimal("0.01")

def q2(v: Decimal) -> Decimal:
    if v is None:
        return Decimal("0.00")
    return (Decimal(v)).quantize(MONEY, rounding=ROUND_HALF_UP)


# ======================================================================
#                        REFERENCE TABLES
# ======================================================================

class JobRate(models.Model):
    """Base hourly rate by job/role (e.g., DEV, DESIGN, PM)."""
    code = models.SlugField(max_length=40, unique=True)  # 'dev', 'design'
    name = models.CharField(max_length=120)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "code")

    def __str__(self):
        return f"{self.name} @ {self.hourly_rate}"


class BaseSetting(models.Model):
    """Base price 'addon' applied per line item (your 'base setting' amount)."""
    code = models.SlugField(max_length=60, unique=True)  # 'vite-app', 'branding-kit'
    name = models.CharField(max_length=160)
    base_rate = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return f"{self.name} (base {self.base_rate})"


class Discount(models.Model):
    class Kind(models.TextChoices):
        PERCENT = "PERCENT", "Percent"
        FIXED   = "FIXED",   "Fixed amount"

    name  = models.CharField(max_length=120)
    code  = models.SlugField(max_length=40, unique=True)  # 'spring-10'
    kind  = models.CharField(max_length=10, choices=Kind.choices, default=Kind.PERCENT)
    value = models.DecimalField(max_digits=10, decimal_places=2)  # percent or fixed amount
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("code",)

    def __str__(self):
        return f"{self.name} ({self.code})"
    
class CatalogItem(models.Model):
    """
    One pickable item that *bundles* a job_rate + base_setting,
    plus sensible defaults for hours and quantity.
    """
    code         = models.SlugField(max_length=80, unique=True)
    name         = models.CharField(max_length=160)
    description  = models.TextField(blank=True)

    job_rate     = models.ForeignKey(JobRate, on_delete=models.PROTECT, related_name="catalog_items")
    base_setting = models.ForeignKey(BaseSetting, on_delete=models.PROTECT, related_name="catalog_items")

    default_hours    = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    default_quantity = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))

    is_active   = models.BooleanField(default=True)
    tags        = models.CharField(max_length=200, blank=True)
    sort_order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return f"{self.name} [{self.code}]"

class CostTier(models.Model):
    """
    Buckets a project by total cost. Used for quick 'walkaway' estimates.
    Example tiers:
      - Tier 1:  500 – 1,250
      - Tier 2:  1,251 – 3,000
      - Tier 3:  3,001 – 7,500
    """
    code        = models.SlugField(max_length=40, unique=True)   # e.g., "tier-1"
    label       = models.CharField(max_length=80)                # e.g., "Tier 1"
    min_total   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    max_total   = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                      help_text="Leave blank for 'no upper limit'.")
    notes       = models.TextField(blank=True)
    sort_order  = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "min_total", "code")

    def __str__(self):
        hi = "∞" if self.max_total is None else f"{self.max_total:.2f}"
        return f"{self.label} ({self.min_total:.2f}–{hi})"

    def clean(self):
        # Basic sanity checks
        if self.max_total is not None and self.max_total <= self.min_total:
            raise ValidationError("max_total must be greater than min_total (or empty).")

    @classmethod
    def for_amount(cls, amount: Decimal):
        """
        Return the active tier that contains 'amount', or None.
        Inclusive lower bound; inclusive upper bound if provided.
        """
        amount = Decimal(amount or 0)
        # Try exact window first
        tier = (cls.objects
                  .filter(is_active=True, min_total__lte=amount)
                  .filter(models.Q(max_total__isnull=True) | models.Q(max_total__gte=amount))
                  .order_by("sort_order", "min_total")
                  .first())
        return tier


# ======================================================================
#                           DRAFT / CHECKLIST
# ======================================================================

class ProposalDraft(models.Model):
    class DepositType(models.TextChoices):
        NONE    = "NONE",    "None"
        PERCENT = "PERCENT", "Percent"
        FIXED   = "FIXED",   "Fixed"

    company    = models.ForeignKey("companyApp.Company", on_delete=models.CASCADE, related_name="pricing_drafts")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    title     = models.CharField(max_length=200)
    currency  = models.CharField(max_length=8, default="USD")

    # Optional quick contact capture before there’s a formal contact
    contact_name  = models.CharField(max_length=160, blank=True)
    contact_email = models.EmailField(blank=True)

    # Totals
    subtotal        = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    discount        = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total           = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # Deposit
    deposit_type    = models.CharField(max_length=10, choices=DepositType.choices, default=DepositType.NONE)
    deposit_value   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))  # percent or fixed
    deposit_amount  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    remaining_due   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # Estimate / Tiering
    estimate_tier  = models.ForeignKey("CostTier", null=True, blank=True, on_delete=models.SET_NULL, related_name="drafts")
    estimate_low   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    estimate_high  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    estimate_manual = models.BooleanField(
        default=False,
        help_text="If checked, keep the selected tier and don't auto-update from totals."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Draft: {self.company.name} · {self.title}"

    # --- Core math ---
    def compute_line_total(self, *, hours, qty, job_rate: "JobRate", base_setting: "BaseSetting") -> Decimal:
        """
        Formula:
        line_total = (hours_to_complete * number_of_items * job_hourly_rate) + base_rate
        """
        hours = Decimal(hours or 0)
        qty   = Decimal(qty or 0)
        hr    = Decimal(job_rate.hourly_rate if job_rate else 0)
        base  = Decimal(base_setting.base_rate if base_setting else 0)
        return q2((hours * qty * hr) + base)

    def compute_discount_amount(self, base: Decimal) -> Decimal:
        if not self.discount or not self.discount.is_active:
            return Decimal("0.00")
        if self.discount.kind == Discount.Kind.PERCENT:
            return q2((base or 0) * (self.discount.value or 0) / Decimal("100"))
        return q2(self.discount.value or 0)

    def compute_deposit_amount(self, grand_total: Decimal) -> Decimal:
        if self.deposit_type == self.DepositType.PERCENT:
            return q2((grand_total or 0) * (self.deposit_value or 0) / Decimal("100"))
        if self.deposit_type == self.DepositType.FIXED:
            return q2(self.deposit_value or 0)
        return Decimal("0.00")
    
    def update_estimate_from_tiers(self, *, use_total=True, save=True):
        """
        If estimate_manual is True, keep the selected estimate_tier and just
        refresh estimate_low/high from it. Otherwise, auto-pick the tier from totals.
        """
        amount = self.total if use_total else self.subtotal

        if self.estimate_manual and self.estimate_tier_id:
            tier = self.estimate_tier  # respect manual choice
        else:
            tier = CostTier.for_amount(amount)
            self.estimate_tier = tier  # auto-pick

        if tier:
            self.estimate_low = tier.min_total or Decimal("0.00")
            self.estimate_high = tier.max_total or amount  # if open-ended, show current as an 'up to'
        else:
            self.estimate_low = Decimal("0.00")
            self.estimate_high = Decimal("0.00")

        if save:
            self.save(update_fields=["estimate_tier", "estimate_low", "estimate_high", "updated_at"])
        return tier


    def recalc_totals(self, *, save=True):
        line_sum = Decimal("0.00")
        for li in self.items.all():
            line_sum += q2(li.line_total)

        self.subtotal = q2(line_sum)
        self.discount_amount = q2(self.compute_discount_amount(self.subtotal))

        base_total = q2(self.subtotal - self.discount_amount)
        self.total = base_total  # no tax layer yet; easy to add later

        self.deposit_amount = q2(self.compute_deposit_amount(self.total))
        self.remaining_due  = q2(self.total - self.deposit_amount)

        if save:
            self.save(update_fields=[
                "subtotal", "discount_amount", "total",
                "deposit_amount", "remaining_due", "updated_at"
            ])
        self.update_estimate_from_tiers(save=True)
        return self.total

    @transaction.atomic
    def convert_to_proposal(self, *, actor=None):
        """
        Create a Proposal snapshot (final) from this Draft for sending/signing.
        Fully compatible with invoiceApp.Invoice.from_proposal().
        """
        prop = Proposal.objects.create(
            company=self.company,
            created_by=actor,
            title=self.title,
            currency=self.currency,
            amount_subtotal=self.subtotal,
            amount_tax=Decimal("0.00"),          # no tax layer in draft yet; safe default
            discount_total=self.discount_amount,
            amount_total=self.total,
            deposit_type=self.deposit_type,
            deposit_value=self.deposit_value,
            deposit_amount=self.deposit_amount,
            remaining_due=self.remaining_due,
            converted_from=self,
        )
        # Snapshot draft items → proposal items.
        # Also populate unit_price/subtotal so invoiceApp can copy directly.
        for li in self.items.all().order_by("sort_order", "pk"):
            ProposalLineItem.objects.create(
                proposal=prop,
                sort_order=li.sort_order,
                name=li.name,
                description=li.description,
                hours=li.hours,
                quantity=li.quantity,
                job_rate=li.job_rate,
                base_setting=li.base_setting,
                line_total=li.line_total,
                # Invoice-compat fields:
                unit_price=li.line_total,   # treat as a single unit price
                subtotal=li.line_total,     # quantity considered 1 for invoice copy
            )

        # Snapshot discount (if any) so invoiceApp can copy applied_discounts
        if self.discount and self.discount_amount:
            ProposalAppliedDiscount.objects.create(
                proposal=prop,
                discount_code=self.discount.code,
                name=self.discount.name,
                kind=self.discount.kind,
                value=self.discount.value,
                amount_applied=self.discount_amount,
                sort_order=0,
            )

        ProposalEvent.objects.create(proposal=prop, kind=ProposalEvent.Kind.CREATED, actor=actor)
        return prop


class DraftItem(models.Model):
    """
    A chosen item inside a draft. Staff picks a CatalogItem (bundled job rate + base fee),
    then only adjust hours and quantity. Name/description/job_rate/base_setting are snapshotted
    from the catalog for transparency and stability.
    """
    draft        = models.ForeignKey(ProposalDraft, on_delete=models.CASCADE, related_name="items")

    # Pickable preset that bundles job_rate + base_setting (+ defaults)
    catalog_item = models.ForeignKey(
        "CatalogItem",
        on_delete=models.PROTECT,
        related_name="draft_items",
        help_text="Choose from the predefined items list."
    )

    # Snapshotted display fields (auto-filled from catalog)
    name         = models.CharField(max_length=160)
    description  = models.TextField(blank=True)

    # Snapshotted pricing components (auto-set from catalog)
    job_rate     = models.ForeignKey(JobRate, on_delete=models.PROTECT, related_name="draft_items")
    base_setting = models.ForeignKey(BaseSetting, on_delete=models.PROTECT, related_name="draft_items")

    # Only these are editable per draft
    hours    = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))

    # Computed
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return f"{self.name} · {self.draft}"

    # ----- internal helpers -----
    def _apply_catalog(self):
        """
        Keep the bundled parts in sync with the chosen catalog item.
        Name/description/rate/base are always snapshotted from the catalog.
        Hours/quantity defaults are applied only on initial create.
        """
        c = self.catalog_item
        if not c:
            return
        # snapshot identity/pricing bits
        self.name = c.name
        self.description = c.description
        self.job_rate = c.job_rate
        self.base_setting = c.base_setting

    # ----- persistence -----
    def save(self, *args, **kwargs):
        creating = not bool(self.pk)

        # 1) snapshot from catalog (name/desc/rate/base)
        self._apply_catalog()

        # 2) on create, if hours/quantity look like defaults, use catalog defaults
        if creating:
            if (self.hours is None) or (self.hours == Decimal("0.00")) or (self.hours == Decimal("1.00")):
                self.hours = self.catalog_item.default_hours
            if (self.quantity is None) or (self.quantity == Decimal("0.00")) or (self.quantity == Decimal("1.00")):
                self.quantity = self.catalog_item.default_quantity

        # 3) compute by formula: (hours * qty * job_rate.hourly_rate) + base_setting.base_rate
        self.line_total = self.draft.compute_line_total(
            hours=self.hours,
            qty=self.quantity,
            job_rate=self.job_rate,
            base_setting=self.base_setting,
        )

        super().save(*args, **kwargs)

        # 4) refresh draft totals
        self.draft.recalc_totals(save=True)



# ======================================================================
#                             PROPOSAL (FINAL)
# ======================================================================

def _signing_base() -> str:
    return getattr(settings, "PROPOSAL_SIGNING_URL_BASE", "").rstrip("/")


class Proposal(models.Model):
    """Final proposal artifact with signing, recipients, events, and invoice linkage."""
    company     = models.ForeignKey("companyApp.Company", on_delete=models.CASCADE, related_name="simple_proposals")
    created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProposalViewer",
        related_name="proposals_shared_with",
        blank=True,
    )

    def __str__(self):
        return f"Proposal {self.code} — {self.company.name}"

    title       = models.CharField(max_length=200)
    currency    = models.CharField(max_length=8, default="USD")

    amount_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_tax      = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))  # << added
    discount_total  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    amount_total    = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    deposit_type   = models.CharField(max_length=10, default=ProposalDraft.DepositType.NONE, choices=ProposalDraft.DepositType.choices)
    deposit_value  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    remaining_due  = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    converted_from = models.ForeignKey(ProposalDraft, null=True, blank=True, on_delete=models.SET_NULL, related_name="proposals")

    # Signing fields
    sign_token       = models.CharField(max_length=64, unique=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Lifecycle stamps
    sent_at    = models.DateTimeField(null=True, blank=True)
    viewed_at  = models.DateTimeField(null=True, blank=True)
    signed_at  = models.DateTimeField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.company.name} · {self.title}"

    # ---- Signing / lifecycle helpers ----
    def ensure_signing_link(self, *, hours_valid: int = 336):  # default 14 days
        if not self.sign_token:
            self.sign_token = secrets.token_urlsafe(32)  # ~43 chars, fits in 64
        if not self.token_expires_at:
            self.token_expires_at = timezone.now() + timezone.timedelta(hours=hours_valid)
        self.save(update_fields=["sign_token", "token_expires_at", "updated_at"])
        base = _signing_base()
        return f"{base}/{self.sign_token}" if base else self.sign_token

    def get_signing_url(self) -> str:
        base = _signing_base()
        if not self.sign_token:
            self.ensure_signing_link()
        return f"{base}/{self.sign_token}" if base else self.sign_token

    def mark_sent(self, *, actor=None, messenger_kwargs: dict | None = None):
        """
        Record sent_at + event; optional messenger hook via settings.PROPOSAL_MESSENGER.
        """
        self.ensure_signing_link()
        if not self.sent_at:
            self.sent_at = timezone.now()
        self.save(update_fields=["sent_at", "updated_at"])

        # messenger hook (optional)
        hook_path = getattr(settings, "PROPOSAL_MESSENGER", "")
        if hook_path:
            try:
                # Lazily resolve to avoid import cycles
                if ":" in hook_path:
                    mod_path, fn_name = hook_path.split(":", 1)
                else:
                    mod_path, fn_name = hook_path.rsplit(".", 1)
                mod = __import__(mod_path, fromlist=[fn_name])
                hook = getattr(mod, fn_name)
                emails = list(self.recipients.values_list("email", flat=True)) or []
                hook(self, emails, self.get_signing_url(), **(messenger_kwargs or {}))
            except Exception as e:
                ProposalEvent.objects.create(
                    proposal=self, kind=ProposalEvent.Kind.UPDATED, actor=actor,
                    data={"warning": f"Messenger hook failed: {e!r}"}
                )

        ProposalEvent.objects.create(proposal=self, kind=ProposalEvent.Kind.SENT, actor=actor)
        return self.sent_at

    def mark_viewed(self, *, ip=None, actor=None):
        first = False
        if not self.viewed_at:
            first = True
            self.viewed_at = timezone.now()
            self.save(update_fields=["viewed_at", "updated_at"])
        ProposalEvent.objects.create(
            proposal=self, kind=ProposalEvent.Kind.VIEWED, actor=actor,
            ip_address=ip, data={"first_time": first}
        )
        return first

    def mark_signed(self, *, actor=None, ip=None, signature_payload=None, due_date=None, customer_user=None):
        """
        Called when client signs via the (future) signing page.
        Also creates the deposit invoice immediately via invoiceApp.Invoice.from_proposal().
        """
        if not self.signed_at:
            self.signed_at = timezone.now()
            self.save(update_fields=["signed_at", "updated_at"])

        # Create the deposit invoice (real invoice model)
        self.create_deposit_invoice(actor=actor, due_date=due_date, customer_user=customer_user)

        ProposalEvent.objects.create(
            proposal=self, kind=ProposalEvent.Kind.SIGNED, actor=actor,
            ip_address=ip, data={"signature": signature_payload}
        )
        return self.signed_at

    def create_deposit_invoice(self, *, actor=None, due_date=None, customer_user=None):
        """
        Uses invoiceApp.Invoice.from_proposal() to create an invoice for this proposal.
        The Invoice factory copies line items & applied discounts and snapshots minimum_due.
        """
        from invoiceApp.models import Invoice  # local import to avoid circulars

        inv = Invoice.from_proposal(
            self,
            created_by=actor,
            due_date=due_date,
            customer_user=customer_user,
        )
        # If you want to ensure 'minimum_due' equals deposit explicitly, you can:
        # inv.minimum_due = self.deposit_amount or Decimal("0.00")
        # inv.save(update_fields=["minimum_due", "updated_at"])
        return inv


class ProposalLineItem(models.Model):
    proposal     = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="line_items")
    sort_order   = models.PositiveIntegerField(default=0)

    name         = models.CharField(max_length=160)
    description  = models.TextField(blank=True)

    # Draft math (kept for transparency)
    hours        = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    quantity     = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("1.00"))
    job_rate     = models.ForeignKey(JobRate, on_delete=models.PROTECT, related_name="proposal_items")
    base_setting = models.ForeignKey(BaseSetting, on_delete=models.PROTECT, related_name="proposal_items")
    line_total   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # Invoice-compat fields expected by invoiceApp.Invoice.from_proposal()
    unit_price   = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    subtotal     = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ("sort_order", "pk")

    def __str__(self):
        return f"{self.name} ({self.line_total})"


class ProposalAppliedDiscount(models.Model):
    """
    Snapshot of discounts applied on a proposal so invoiceApp can copy them.
    """
    proposal       = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="applied_discounts")
    discount_code  = models.SlugField(max_length=40)
    name           = models.CharField(max_length=120)
    kind           = models.CharField(max_length=10, choices=Discount.Kind.choices)
    value          = models.DecimalField(max_digits=10, decimal_places=2)
    amount_applied = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    sort_order     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return f"{self.name} ({self.discount_code})"


class ProposalRecipient(models.Model):
    proposal    = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="recipients")
    name        = models.CharField(max_length=160, blank=True)
    email       = models.EmailField()
    is_primary  = models.BooleanField(default=True)
    delivered_at   = models.DateTimeField(null=True, blank=True)
    last_opened_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-is_primary", "email")
        unique_together = (("proposal", "email"),)

    def __str__(self):
        return f"{self.email} · {self.proposal}"
    
class ProposalViewer(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="allowed_viewers")
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="allowed_proposals")

    class Meta:
        unique_together = [("proposal", "user")]
        indexes = [models.Index(fields=["proposal", "user"])]

    def __str__(self):
        return f"{self.user} can view {self.proposal}"


class ProposalEvent(models.Model):
    class Kind(models.TextChoices):
        CREATED  = "CREATED",  "Created"
        SENT     = "SENT",     "Sent"
        VIEWED   = "VIEWED",   "Viewed"
        SIGNED   = "SIGNED",   "Signed"
        UPDATED  = "UPDATED",  "Updated"
        COMMENT  = "COMMENT",  "Comment"

    proposal   = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="events")
    kind       = models.CharField(max_length=20, choices=Kind.choices)
    at         = models.DateTimeField(auto_now_add=True)
    actor      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    data       = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ("-at", "pk")

    def __str__(self):
        return f"{self.proposal} · {self.kind} @ {self.at:%Y-%m-%d %H:%M}"
