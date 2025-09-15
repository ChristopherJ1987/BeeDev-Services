# companyApp/models.py
import os, uuid, datetime
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.templatetags.static import static
from django.utils.text import slugify

# ---------- Validators / helpers ----------
ALLOWED_LOGO_EXTS = ["jpg", "jpeg", "png", "webp"]
MAX_LOGO_BYTES = 3 * 1024 * 1024  # 3 MB

def validate_logo_size(f):
    if f.size and f.size > MAX_LOGO_BYTES:
        raise ValidationError(f"Logo too large (>{MAX_LOGO_BYTES//1024//1024}MB).")

def logo_upload_to(instance, filename):
    """
    MEDIA path: company_logos/YYYY/MM/<slug>-<uuid>.<ext>
    Uses company name if slug isn't set yet (first save).
    """
    ext = os.path.splitext(filename)[1].lower().lstrip(".") or "png"
    if ext not in ALLOWED_LOGO_EXTS:
        ext = "png"
    today = datetime.date.today()
    base = slugify(getattr(instance, "slug", "") or getattr(instance, "name", "") or "company")
    return f"company_logos/{today.year}/{today.month:02d}/{base}-{uuid.uuid4().hex}.{ext}"


# =======================================================================
#                              COMPANY
# =======================================================================
class Company(models.Model):
    # Account-level status (relationship with you)
    class Status(models.TextChoices):
        PROSPECT = "PROSPECT", "Prospect"
        ACTIVE   = "ACTIVE",   "Active"
        INACTIVE = "INACTIVE", "Inactive"

    # Project/pipeline status (from spreadsheet "Status")
    class PipelineStatus(models.TextChoices):
        NEW         = "NEW",         "New"
        HOLDING     = "HOLDING",     "Holding"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        ONGOING     = "ONGOING",     "On Going"
        FINISHED    = "FINISHED",    "Finished"
        INACTIVE    = "INACTIVE",    "Inactive"

    name  = models.CharField(max_length=200, unique=True)
    slug  = models.SlugField(max_length=220, unique=True, blank=True)

    # Pre-account primary contact info (optional; use CompanyContact for multiples)
    primary_contact_name = models.CharField(max_length=120, blank=True)
    primary_email        = models.EmailField(blank=True)
    phone                = models.CharField(max_length=30, blank=True)

    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city          = models.CharField(max_length=120, blank=True)
    state_region  = models.CharField(max_length=120, blank=True)
    postal_code   = models.CharField(max_length=20, blank=True)
    country       = models.CharField(max_length=120, blank=True, default="USA")

    website = models.URLField(blank=True)

    logo = models.ImageField(
        upload_to=logo_upload_to, blank=True, null=True,
        validators=[FileExtensionValidator(ALLOWED_LOGO_EXTS), validate_logo_size],
        help_text="PNG/JPEG/WebP, up to 3MB."
    )
    logo_external_url = models.URLField(
        blank=True,
        help_text="Optional external logo URL (e.g., Google Drive shared link)."
    )

    # Relationship + pipeline
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.PROSPECT)
    pipeline_status = models.CharField(max_length=20, choices=PipelineStatus.choices, blank=True, default="")

    # From sheet: link to the consultation/profile sheet
    consultation_sheet_url = models.URLField(blank=True)
    first_contact_at = models.DateField(null=True, blank=True)
    last_contact_at  = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="companies_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["status"]),
            models.Index(fields=["pipeline_status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "company"
            slug = base
            i = 2
            while Company.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    @property
    def logo_url(self) -> str:
        """
        Priority: external URL (Drive) > uploaded logo (MEDIA) > static placeholder.
        Safe for templates.
        """
        if getattr(self, "logo_external_url", ""):
            return self.logo_external_url
        try:
            if self.logo:
                return self.logo.url
        except Exception:
            pass
        return static("img/company-logo-placeholder.svg")

# =======================================================================
#                          COMPANY CONTACT
# =======================================================================
class CompanyContact(models.Model):
    """
    Zero or more contacts per company.
    Optionally link to a User after they create an account.
    """
    company   = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    user      = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="company_contacts"
    )

    name      = models.CharField(max_length=120)
    email     = models.EmailField(blank=True)
    phone     = models.CharField(max_length=30, blank=True)
    title     = models.CharField(max_length=120, blank=True)
    is_primary = models.BooleanField(default=False)
    notes     = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-is_primary", "name")
        unique_together = (("company", "email"),)
        indexes = [
            models.Index(fields=["company", "is_primary"]),
            models.Index(fields=["company", "email"]),
        ]

    def __str__(self):
        return f"{self.company.name}: {self.name}"

# =======================================================================
#                          COMPANY LINK
# =======================================================================
class CompanyLink(models.Model):
    """
    Links associated with a Company.
    Some are client-visible; others are internal (employee-only).
    """
    class Visibility(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee only"
        SHARED   = "SHARED",   "Client & Employee"

    class Section(models.TextChoices):
        GENERAL    = "GENERAL",    "General"
        HOSTING    = "HOSTING",    "Hosting / CMS"
        DOMAINS    = "DOMAINS",    "Domains / DNS"
        ANALYTICS  = "ANALYTICS",  "Analytics"
        DESIGN     = "DESIGN",     "Design (Figma, etc.)"
        REPOSITORY = "REPOSITORY", "Repositories"
        ENVIRON    = "ENVIRON",    "Environments"
        DOCS       = "DOCS",       "Docs / Drive"
        OTHER      = "OTHER",      "Other"

    company     = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="links")
    label       = models.CharField(max_length=120) # e.g., "Preview Site", "Production", "Figma"
    url         = models.URLField(blank=True)
    notes       = models.TextField(blank=True)
    section     = models.CharField(max_length=20, choices=Section.choices, default=Section.GENERAL, blank=True)
    tags        = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags (optional)")
    visibility  = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.EMPLOYEE)
    is_active   = models.BooleanField(default=True)
    sort_order  = models.PositiveIntegerField(default=0)

    # Non-secret hints about credentials
    key_name    = models.CharField(max_length=120, blank=True, help_text="Name of key/credential (do not store secrets)")
    key_hint    = models.CharField(max_length=200, blank=True, help_text="Where the key lives (e.g., vault ref)")

    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="company_links_created",
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "label")
        unique_together = (("company", "label", "section"),)
        indexes = [
            models.Index(fields=["company", "visibility", "is_active", "sort_order"]),
            models.Index(fields=["company", "section"]),
        ]

    def __str__(self):
        return f"{self.company.name}: {self.label}"
