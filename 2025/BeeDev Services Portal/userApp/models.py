# userApp/models.py
import os, uuid, datetime
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.templatetags.static import static

# ---------- Validators / helpers ----------
ALLOWED_IMAGE_EXTS = ["jpg", "jpeg", "png", "webp"]
MAX_IMAGE_BYTES = 3 * 1024 * 1024  # 3 MB

def validate_image_size(f):
    if f.size and f.size > MAX_IMAGE_BYTES:
        raise ValidationError(f"Image too large (>{MAX_IMAGE_BYTES//1024//1024}MB).")

def avatar_upload_to(instance, filename):
    """
    Store at: media/profiles/YYYY/MM/<userId>-<uuid>.<ext>
    Non-allowed extensions are coerced to .jpg (validation still enforces allowed types).
    Works for both ClientProfile and EmployeeProfile (expects .user).
    """
    ext = os.path.splitext(filename)[1].lower().lstrip(".") or "jpg"
    if ext not in ALLOWED_IMAGE_EXTS:
        ext = "jpg"
    today = datetime.date.today()
    user_id = getattr(instance.user, "id", "anon")
    return f"profiles/{today.year}/{today.month:02d}/{user_id}-{uuid.uuid4().hex}.{ext}"


# =======================================================================
#                               USER
# =======================================================================
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # hashes password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Roles.OWNER)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"
        CLIENT   = "CLIENT",   "Client"
        ADMIN    = "ADMIN",    "Admin"
        OWNER    = "OWNER",    "Owner"
        HR       = "HR",       "HR"

    email = models.EmailField(unique=True)
    role  = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CLIENT)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    # --- Name helpers ---
    @property
    def preferred_name(self) -> str:
        """First name if present; otherwise username."""
        return (self.first_name or "").strip() or self.username

    @property
    def display_name(self) -> str:
        """Full name if present; otherwise username."""
        full = f"{(self.first_name or '').strip()} {(self.last_name or '').strip()}".strip()
        return full or self.username

    def fullName(self):
        # legacy helper; Django also has get_full_name()
        return f"{self.first_name} {self.last_name}"

    # --- Avatar helper ---
    @property
    def avatar_url(self) -> str:
        """
        Always returns something renderable:
        - employee profile image if present
        - else client profile image if present
        - else a static placeholder
        """
        try:
            ep = getattr(self, "employee_profile", None)
            if ep and ep.profile_image:
                return ep.profile_image.url
        except Exception:
            pass
        try:
            cp = getattr(self, "profile", None)
            if cp and cp.profile_image:
                return cp.profile_image.url
        except Exception:
            pass
        return static("img/avatar.svg")  # ensure this exists in your static files

    # --- Company / membership helpers (multi-company) ---
    def companies_qs(self):
        """
        Active companies this user belongs to (via companyApp.CompanyMembership).
        """
        from companyApp.models import Company  # local import avoids circulars
        return Company.objects.filter(memberships__user=self, memberships__is_active=True)

    def membership_for(self, company):
        """
        Return CompanyMembership or None for a given company.
        """
        return getattr(self, "company_memberships", None).filter(company=company, is_active=True).first()

    def is_company_admin(self, company):
        """
        True if Account Admin or Manager for this company.
        """
        mem = self.membership_for(company)
        if not mem:
            return False
        return mem.role in {"ACCOUNT_ADMIN", "MANAGER"}

    def can_view_company_invoices(self, company):
        mem = self.membership_for(company)
        if not mem:
            return False
        return mem.role in {"ACCOUNT_ADMIN", "MANAGER"} or mem.can_view_invoices

    def can_view_company_proposals(self, company):
        mem = self.membership_for(company)
        if not mem:
            return False
        return mem.role in {"ACCOUNT_ADMIN", "MANAGER"} or mem.can_view_proposals


# =======================================================================
#                             PROFILES
# =======================================================================
class ClientProfile(models.Model):
    """
    Client profile is now company-agnostic; company membership is modeled by companyApp.CompanyMembership.
    Keep free-form company_* fields for pre-signup imports or defaults.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    # Profile image
    profile_image = models.ImageField(
        upload_to=avatar_upload_to,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(ALLOWED_IMAGE_EXTS), validate_image_size],
        help_text="JPEG/PNG/WebP, up to 3MB.",
    )

    # ---- NO company FK here (multi-company via memberships) ----

    # Optional company/contact defaults (not authoritative)
    company_name  = models.CharField(max_length=200, blank=True)
    company_email = models.EmailField(blank=True)  # separate from user.email
    phone         = models.CharField(max_length=30, blank=True)

    # Address (billing/contact default)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city          = models.CharField(max_length=120, blank=True)
    state_region  = models.CharField(max_length=120, blank=True)
    postal_code   = models.CharField(max_length=20, blank=True)
    country       = models.CharField(max_length=120, blank=True, default="USA")

    # Timestamps
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

    # Convenience: companies via memberships
    def companies_qs(self):
        return self.user.companies_qs()


class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile")

    # Profile image
    profile_image = models.ImageField(
        upload_to=avatar_upload_to,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(ALLOWED_IMAGE_EXTS), validate_image_size],
        help_text="JPEG/PNG/WebP, up to 3MB.",
    )

    # Employee details
    job_title      = models.CharField(max_length=120, blank=True)
    work_email     = models.EmailField(blank=True)
    work_phone     = models.CharField(max_length=30, blank=True)
    discord_handle = models.CharField(max_length=60, blank=True)

    # Address (optional)
    address_line1  = models.CharField(max_length=200, blank=True)
    address_line2  = models.CharField(max_length=200, blank=True)
    city           = models.CharField(max_length=120, blank=True)
    state_region   = models.CharField(max_length=120, blank=True)
    postal_code    = models.CharField(max_length=20, blank=True)
    country        = models.CharField(max_length=120, blank=True, default="USA")

    # Internal notes (admin only)
    notes_internal = models.TextField(blank=True)

    # Timestamps
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"EmployeeProfile({self.user.username})"
