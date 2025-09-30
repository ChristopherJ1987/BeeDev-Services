# ticketApp/models.py
import os, uuid, datetime
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

ALLOWED_FILE_EXTS = ["pdf", "png", "jpg", "jpeg", "webp", "txt", "docx", "xlsx"]
MAX_FILE_BYTES = 20 * 1024 * 1024  # 20MB

def validate_file_size(f):
    if f and f.size and f.size > MAX_FILE_BYTES:
        raise ValidationError(f"File too large (> {MAX_FILE_BYTES//1024//1024}MB).")

def ticket_upload_to(instance, filename):
    # MEDIA: tickets/<company-or-project>/<ticket-key>/<uuid>.<ext>
    comp = getattr(instance.message.ticket.company, "slug", None) or f"company-{instance.message.ticket.company_id}"
    key  = instance.message.ticket.public_key or f"t-{instance.message.ticket_id or 'new'}"
    ext  = os.path.splitext(filename)[1].lower()
    today = datetime.date.today()
    return f"tickets/{comp}/{key}/{today.year}/{today.month:02d}/{uuid.uuid4().hex}{ext}"


class Ticket(models.Model):
    class Status(models.TextChoices):
        NEW        = "NEW",        "New"
        OPEN       = "OPEN",       "Open"
        PENDING    = "PENDING",    "Pending Client"
        INPROGRESS = "INPROGRESS", "In Progress"
        RESOLVED   = "RESOLVED",   "Resolved"
        CLOSED     = "CLOSED",     "Closed"

    class Priority(models.TextChoices):
        LOW    = "LOW",    "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH   = "HIGH",   "High"
        URGENT = "URGENT", "Urgent"

    class Category(models.TextChoices):
        CONTENT = "CONTENT", "Content"
        BUG     = "BUG",     "Bug"
        REQUEST = "REQUEST", "Feature/Request"
        BILLING = "BILLING", "Billing"
        OTHER   = "OTHER",   "Other"

    company      = models.ForeignKey("companyApp.Company", on_delete=models.CASCADE, related_name="tickets")
    project      = models.ForeignKey("projectApp.Project", null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets")

    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets_opened")
    created_by    = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets_created")
    assigned_to   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets_assigned")

    public_key   = models.CharField(max_length=24, unique=True, blank=True, help_text="e.g., T-2025-AB12CD34")
    subject      = models.CharField(max_length=200)
    description  = models.TextField(blank=True)

    status       = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    priority     = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    category     = models.CharField(max_length=10, choices=Category.choices, default=Category.OTHER)

    last_client_reply_at = models.DateTimeField(null=True, blank=True)
    closed_at    = models.DateTimeField(null=True, blank=True)

    watchers     = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="ticket_watchlist")

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "pk")
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["public_key"]),
        ]

    def __str__(self):
        return f"{self.public_key or f'Ticket#{self.pk}'} · {self.subject}"

    def save(self, *args, **kwargs):
        if not self.public_key:
            # Simple readable key: T-YYYY-<8 hex>
            self.public_key = f"T-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def is_open(self) -> bool:
        return self.status not in {self.Status.RESOLVED, self.Status.CLOSED}


class TicketMessage(models.Model):
    class AuthorKind(models.TextChoices):
        STAFF  = "STAFF",  "Staff"
        CLIENT = "CLIENT", "Client"

    ticket      = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="ticket_messages")
    author_kind = models.CharField(max_length=8, choices=AuthorKind.choices, default=AuthorKind.STAFF)

    body        = models.TextField(blank=True)
    is_internal = models.BooleanField(default=False, help_text="If true, client cannot see this message")

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "pk")

    def __str__(self):
        return f"{self.ticket.public_key}: {self.author_kind} ({'internal' if self.is_internal else 'shared'})"
    
    def clean(self):
        # Clients cannot create internal-only messages
        if self.author_kind == self.AuthorKind.CLIENT and self.is_internal:
            raise ValidationError({"is_internal": "Client messages cannot be marked internal."})

    def save(self, *args, **kwargs):
        self.full_clean(exclude=None)
        super().save(*args, **kwargs)
        # Update ticket “last client reply” for SLA/reporting
        if self.author_kind == self.AuthorKind.CLIENT and not self.is_internal:
            self.ticket.last_client_reply_at = self.created_at
            self.ticket.save(update_fields=["last_client_reply_at", "updated_at"])


class TicketAttachment(models.Model):
    message = models.ForeignKey(TicketMessage, on_delete=models.CASCADE, related_name="attachments")
    file    = models.FileField(
        upload_to=ticket_upload_to,
        validators=[FileExtensionValidator(ALLOWED_FILE_EXTS), validate_file_size],
    )
    original_name = models.CharField(max_length=200, blank=True)
    uploaded_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name or os.path.basename(self.file.name)


class TicketEvent(models.Model):
    class Kind(models.TextChoices):
        CREATED    = "CREATED",    "Created"
        ASSIGNED   = "ASSIGNED",   "Assigned"
        STATUS     = "STATUS",     "Status Change"
        COMMENT    = "COMMENT",    "Comment"
        ATTACHMENT = "ATTACHMENT", "Attachment"
        CLOSED     = "CLOSED",     "Closed"

    ticket    = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="events")
    kind      = models.CharField(max_length=12, choices=Kind.choices)
    at        = models.DateTimeField(auto_now_add=True)
    actor     = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    data      = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ("-at", "pk")

    def __str__(self):
        return f"{self.ticket.public_key} · {self.kind} @ {self.at:%Y-%m-%d %H:%M}"
