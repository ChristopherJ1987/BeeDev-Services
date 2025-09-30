# announceApp/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Announcement(models.Model):
    class Audience(models.TextChoices):
        ALL      = "ALL", "All Users"
        EMPLOYEE = "EMPLOYEE", "Employees"
        CLIENT   = "CLIENT", "Clients"
        PUBLIC   = "PUBLIC", "Public / Logged-out"

    class Severity(models.TextChoices):
        INFO    = "INFO", "Info"
        SUCCESS = "SUCCESS", "Success"
        WARNING = "WARNING", "Warning"
        DANGER  = "DANGER", "Danger"

    slug         = models.SlugField(max_length=80, unique=True, help_text="Stable id for dismissing in localStorage.")
    title        = models.CharField(max_length=140, blank=True)
    message_html = models.TextField(help_text="Supports HTML")
    audience     = models.CharField(max_length=12, choices=Audience.choices, default=Audience.ALL)
    severity     = models.CharField(max_length=8, choices=Severity.choices, default=Severity.INFO)

    is_active    = models.BooleanField(default=True)
    dismissible  = models.BooleanField(default=True)
    starts_at    = models.DateTimeField(null=True, blank=True)
    ends_at      = models.DateTimeField(null=True, blank=True)
    priority     = models.IntegerField(default=0, help_text="Lower shows first")

    link_url     = models.URLField(blank=True)
    link_text    = models.CharField(max_length=60, blank=True)

    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("priority", "-updated_at")

    def __str__(self):
        return f"{self.slug} · {self.audience} · active={self.is_active}"

    def is_current(self, now=None):
        now = now or timezone.now()
        if not self.is_active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return True

class Version(models.Model):
    slug = models.SlugField(max_length=80, unique=True, help_text="Stable id for dismissing in localStorage.")
    version_num = models.CharField(max_length=255)
    info = models.TextField()
    date_of_release = models.DateField(blank=True, null=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("date_of_release", "-updated_at")
    
    def __str__(self):
        return self.version_num