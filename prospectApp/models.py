from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone
import secrets

class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Prospect(TimeStamped):
    class Status(models.TextChoices):
        NEW = "NEW", "New"
        RESEARCHED = "RES", "Researched"
        READY = "RDY", "Ready to Contact"
        EMAILED = "EML", "Emailed"
        REPLIED = "RPL", "Replied"
        BOUNCED = "BNC", "Bounced"
        UNSUB = "UNS", "Unsubscribed"
        WON = "WON", "Converted"
        LOST = "LST", "Not a Fit"

    full_name   = models.CharField(max_length=120, blank=True)
    company_name= models.CharField(max_length=160, blank=True)
    email       = models.EmailField(unique=True)
    phone       = models.CharField(max_length=40, blank=True)

    address1    = models.CharField(max_length=160, blank=True)
    address2    = models.CharField(max_length=160, blank=True)
    city        = models.CharField(max_length=80,  blank=True)
    state       = models.CharField(max_length=80,  blank=True)
    postal_code = models.CharField(max_length=20,  blank=True)
    country     = models.CharField(max_length=60,  blank=True, default="USA")

    website_url = models.CharField(max_length=300, blank=True, validators=[URLValidator()], help_text="Leave blank if no site")
    notes       = models.TextField(blank=True)

    status      = models.CharField(max_length=3, choices=Status.choices, default=Status.NEW)
    tags        = models.CharField(max_length=200, blank=True, help_text="Comma-separated")

    last_contacted_at = models.DateTimeField(null=True, blank=True)
    next_follow_up_at = models.DateTimeField(null=True, blank=True)

    do_not_contact = models.BooleanField(default=False)
    unsubscribe_token = models.CharField(max_length=32, unique=True, editable=False, blank=True)

    def save(self, *args, **kwargs):
        if not self.unsubscribe_token:
            self.unsubscribe_token = secrets.token_hex(16)
        self.email = (self.email or "").strip().lower()
        super().save(*args, **kwargs)

    @property
    def has_website(self): 
        return bool(self.website_url)

    def __str__(self):
        base = self.company_name or self.full_name or self.email
        return f"{base} ({self.email})"
