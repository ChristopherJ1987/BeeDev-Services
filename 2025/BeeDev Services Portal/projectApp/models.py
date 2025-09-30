# projectApp/models.py
import os, uuid, datetime
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

ALLOWED_DOC_EXTS = ["pdf", "png", "jpg", "jpeg", "webp", "docx", "xlsx", "txt"]
MAX_FILE_BYTES = 20 * 1024 * 1024  # 20MB

def validate_file_size(f):
    if f and f.size and f.size > MAX_FILE_BYTES:
        raise ValidationError(f"File too large (> {MAX_FILE_BYTES//1024//1024}MB).")

def project_upload_to(project_slug: str, folder: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    today = datetime.date.today()
    return f"projects/{project_slug}/{today.year}/{today.month:02d}/{folder}/{uuid.uuid4().hex}{ext}"

def update_attachment_upload_to(instance, filename):
    slug = getattr(instance.update.project, "slug", None) or f"project-{instance.update.project_id}"
    return project_upload_to(slug, "updates", filename)

def link_section_choices():
    return [
        ("GENERAL", "General"),
        ("ENVIRON", "Environments"),
        ("REPOSITORY", "Repositories"),
        ("DESIGN", "Design (Figma, etc.)"),
        ("DOCS", "Docs / Drive"),
        ("OTHER", "Other"),
    ]

class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING   = "PLANNING",   "Planning"
        ACTIVE     = "ACTIVE",     "Active"
        ON_HOLD    = "ON_HOLD",    "On Hold"
        COMPLETE   = "COMPLETE",   "Complete"
        ARCHIVED   = "ARCHIVED",   "Archived"

    class Stage(models.TextChoices):
        DISCOVERY  = "DISCOVERY",  "Discovery"
        DESIGN     = "DESIGN",     "Design"
        BUILD      = "BUILD",      "Build"
        QA         = "QA",         "QA / UAT"
        LAUNCH     = "LAUNCH",     "Launch"
        POST       = "POST",       "Post-Launch"

    company   = models.ForeignKey("companyApp.Company", on_delete=models.CASCADE, related_name="projects")
    proposal  = models.ForeignKey("proposalApp.Proposal", null=True, blank=True, on_delete=models.SET_NULL, related_name="projects")

    name      = models.CharField(max_length=200)
    slug      = models.SlugField(max_length=240, unique=True, blank=True, help_text="Human-friendly project code")

    status    = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    stage     = models.CharField(max_length=20, choices=Stage.choices, blank=True, default="")

    manager   = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="managed_projects")
    description = models.TextField(blank=True)
    scope_summary = models.TextField(blank=True)

    percent_complete = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    start_date       = models.DateField(null=True, blank=True)
    target_launch_date = models.DateField(null=True, blank=True)
    actual_launch_date = models.DateField(null=True, blank=True)

    client_can_view_status      = models.BooleanField(default=True)
    client_can_view_links       = models.BooleanField(default=True)
    client_can_view_description = models.BooleanField(default=False)

    is_active  = models.BooleanField(default=True)
    tags       = models.CharField(max_length=200, blank=True)

    priority = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        help_text="Project urgency (1=highest, 9=lowest)."
    )
    # Whether clients can see the project's numeric priority on client views.
    show_priority_to_client = models.BooleanField(default=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="projects_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("company__name", "name")
        indexes = [models.Index(fields=["company", "status"]), models.Index(fields=["slug"])]

    def __str__(self):
        return f"{self.company.name} · {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.company.name}-{self.name}")[:200] or "project"
            slug = base
            i = 2
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

class ProjectMember(models.Model):
    class Role(models.TextChoices):
        MANAGER = "MANAGER", "Project Manager"
        DESIGN  = "DESIGN",  "Design"
        DEV     = "DEV",     "Developer"
        QA      = "QA",      "QA"
        PM      = "PM",      "Producer/PM"
        CLIENT  = "CLIENT",  "Client"
        OTHER   = "OTHER",   "Other"

    project  = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="members")
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_memberships")
    role     = models.CharField(max_length=16, choices=Role.choices, default=Role.OTHER)
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("project", "user"),)
        ordering = ("project", "role", "user__username")

    def __str__(self):
        return f"{self.project.slug} · {self.user} ({self.role})"

class ProjectTask(models.Model):
    class Status(models.TextChoices):
        TODO        = "TODO",        "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        BLOCKED     = "BLOCKED",     "Blocked"
        DONE        = "DONE",        "Done"
        CANCELED    = "CANCELED",    "Canceled"

    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title     = models.CharField(max_length=240)
    description = models.TextField(blank=True)

    # Independent, numeric task priority (1 = highest)
    priority  = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        help_text="Task priority (1=highest, 9=lowest)."
    )

    status    = models.CharField(max_length=16, choices=Status.choices, default=Status.TODO)

    # Dates & weekly planning
    due_date          = models.DateField(null=True, blank=True)
    planned_week_start = models.DateField(
        null=True, blank=True,
        help_text="Week start (e.g. Monday) this task is planned for."
    )

    # Assignment (keep simple: assign to users on the project)
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="assigned_project_tasks",
        help_text="Team members responsible for this task."
    )

    # Progress & ordering
    estimated_hours   = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    percent_complete  = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    sort_order        = models.PositiveIntegerField(default=0)

    # Client visibility controls
    is_client_visible        = models.BooleanField(
        default=True,
        help_text="If false, clients cannot see this task at all."
    )
    show_priority_to_client  = models.BooleanField(
        default=False,
        help_text="If true AND task is visible, clients can see the task's priority number."
    )

    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="project_tasks_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "project",
            "planned_week_start",
            "priority",     # lower numbers first
            "sort_order",
            "due_date",
            "pk",
        )
        indexes = [
            models.Index(fields=["project", "status"]),
            models.Index(fields=["project", "planned_week_start"]),
            models.Index(fields=["project", "priority"]),
            models.Index(fields=["project", "is_client_visible"]),
        ]

    def __str__(self):
        return f"{self.project.slug} · {self.title}"

    @property
    def is_done(self) -> bool:
        return self.status == self.Status.DONE

class ProjectMilestone(models.Model):
    class State(models.TextChoices):
        PLANNED  = "PLANNED",  "Planned"
        STARTED  = "STARTED",  "Started"
        DONE     = "DONE",     "Done"
        CANCELED = "CANCELED", "Canceled"

    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="milestones")
    name      = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date  = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    state     = models.CharField(max_length=12, choices=State.choices, default=State.PLANNED)

    is_client_visible = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "due_date", "pk")

    def __str__(self):
        return f"{self.project.slug}: {self.name}"

class ProjectUpdate(models.Model):
    class Visibility(models.TextChoices):
        INTERNAL = "INTERNAL", "Internal (staff only)"
        SHARED   = "SHARED",   "Shared with client"

    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="updates")
    title     = models.CharField(max_length=200)
    body      = models.TextField(blank=True)
    visibility= models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.SHARED)

    percent_complete_snapshot = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="project_updates_created")
    posted_at  = models.DateTimeField(auto_now_add=True)
    pinned     = models.BooleanField(default=False)

    class Meta:
        ordering = ("-pinned", "-posted_at", "pk")
        indexes = [models.Index(fields=["project", "visibility", "-posted_at"])]

    def __str__(self):
        return f"{self.project.slug}: {self.title}"

class ProjectUpdateAttachment(models.Model):
    update   = models.ForeignKey(ProjectUpdate, on_delete=models.CASCADE, related_name="attachments")
    file     = models.FileField(upload_to=update_attachment_upload_to,
                                validators=[FileExtensionValidator(ALLOWED_DOC_EXTS), validate_file_size])
    original_name = models.CharField(max_length=200, blank=True)
    uploaded_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name or os.path.basename(self.file.name)

class ProjectEnvironment(models.Model):
    class Kind(models.TextChoices):
        PREVIEW = "PREVIEW", "Preview"
        STAGING = "STAGING", "Staging"
        PROD    = "PROD",    "Production"

    class Health(models.TextChoices):
        UNKNOWN     = "UNKNOWN",     "Unknown"
        UP          = "UP",          "Up"
        DEGRADED    = "DEGRADED",    "Degraded"
        DOWN        = "DOWN",        "Down"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="environments")
    kind    = models.CharField(max_length=10, choices=Kind.choices, default=Kind.PREVIEW)
    url     = models.URLField(blank=True)
    health  = models.CharField(max_length=12, choices=Health.choices, default=Health.UNKNOWN)
    note    = models.CharField(max_length=200, blank=True)

    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = (("project", "kind"),)
        ordering = ("project", "kind")

    def __str__(self):
        return f"{self.project.slug} {self.kind}"
        
class ProjectLink(models.Model):
    class Visibility(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee only"
        SHARED   = "SHARED",   "Client & Employee"

    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="links")
    label     = models.CharField(max_length=120)
    url       = models.URLField(blank=True)
    section   = models.CharField(max_length=20, choices=link_section_choices(), default="GENERAL", blank=True)
    visibility= models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.EMPLOYEE)
    is_active = models.BooleanField(default=True)
    sort_order= models.PositiveIntegerField(default=0)
    notes     = models.TextField(blank=True)

    class Meta:
        ordering = ("sort_order", "label")
        unique_together = (("project", "label", "section"),)

    def __str__(self):
        return f"{self.project.slug}: {self.label}"

class ProjectViewer(models.Model):
    """
    Extra allow-list of users who may view this project (per-project override).
    Useful when not every company member should see this project.
    """
    project = models.ForeignKey("projectApp.Project", on_delete=models.CASCADE, related_name="viewers")
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects_visible")

    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="project_view_grants"
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("project", "user"),)
        indexes = [models.Index(fields=["project", "user"])]

    def __str__(self):
        return f"{self.project.slug} → {self.user}"

class ProjectWeekNote(models.Model):
    project   = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="week_notes")
    week_start = models.DateField(help_text="Normalized to week start (e.g., Monday).")
    body      = models.TextField(blank=True)

    # Visibility mirrors ProjectUpdate style
    class Visibility(models.TextChoices):
        INTERNAL = "INTERNAL", "Internal (staff only)"
        SHARED   = "SHARED",   "Shared with client"

    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.SHARED)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="project_week_notes_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("project", "week_start"),)
        ordering = ("-week_start", "pk")
        indexes = [models.Index(fields=["project", "-week_start"])]

    def __str__(self):
        return f"{self.project.slug} · Week of {self.week_start}"
