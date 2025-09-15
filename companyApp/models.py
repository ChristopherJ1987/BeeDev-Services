# companyApp/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Company(models.Model):
    class Status(models.TextChoices):
        PROSPECT = "PROSPECT", "Prospect"
        ACTIVE   = "ACTIVE",   "Active"
        INACTIVE = "INACTIVE", "Inactive"

    name  = models.CharField(max_length=200, unique=True)
    slug  = models.SlugField(max_length=220, unique=True, blank=True)

    primary_email = models.EmailField(blank=True)
    phone         = models.CharField(max_length=30, blank=True)

    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city          = models.CharField(max_length=120, blank=True)
    state_region  = models.CharField(max_length=120, blank=True)
    postal_code   = models.CharField(max_length=20, blank=True)
    country       = models.CharField(max_length=120, blank=True, default="USA")

    website = models.URLField(blank=True)
    status  = models.CharField(max_length=20, choices=Status.choices, default=Status.PROSPECT)
    notes   = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="companies_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["name"]), models.Index(fields=["slug"])]
        # If you already migrated Company in userApp and want to KEEP the same table without data loss:
        # db_table = "userApp_company"   # <-- optional compatibility trick

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
