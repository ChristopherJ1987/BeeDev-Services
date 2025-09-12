# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)   # 🔒 hashes password
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
        CLIENT = "CLIENT", "Client"
        ADMIN = "ADMIN", "Admin"
        OWNER = "OWNER", "Owner"
        HR = "HR", "HR"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CLIENT)

    # Remove firstName/lastName, AbstractUser already has `first_name` and `last_name`
    # Remove password (it’s handled securely by AbstractUser)

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def fullName(self):
        return f"{self.first_name} {self.last_name}"

class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    # Company / contact
    company_name   = models.CharField(max_length=200, blank=True)
    company_email  = models.EmailField(blank=True)           # optional, separate from user.email
    phone          = models.CharField(max_length=30, blank=True)  # keep simple; validate in form

    # Address
    address_line1  = models.CharField(max_length=200, blank=True)
    address_line2  = models.CharField(max_length=200, blank=True)
    city           = models.CharField(max_length=120, blank=True)
    state_region   = models.CharField(max_length=120, blank=True)
    postal_code    = models.CharField(max_length=20,  blank=True)
    country        = models.CharField(max_length=120, blank=True, default="USA")

    # Timestamps
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
    
class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile")
    job_title      = models.CharField(max_length=120, blank=True)
    work_email     = models.EmailField(blank=True)
    work_phone     = models.CharField(max_length=30, blank=True)
    discord_handle   = models.CharField(max_length=60, blank=True)
    # keep address optional; often not needed for staff
    address_line1  = models.CharField(max_length=200, blank=True)
    address_line2  = models.CharField(max_length=200, blank=True)
    city           = models.CharField(max_length=120, blank=True)
    state_region   = models.CharField(max_length=120, blank=True)
    postal_code    = models.CharField(max_length=20,  blank=True)
    country        = models.CharField(max_length=120, blank=True, default="USA")
    notes_internal = models.TextField(blank=True)  # visible in admin only
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    def __str__(self): return f"EmployeeProfile({self.user.username})"