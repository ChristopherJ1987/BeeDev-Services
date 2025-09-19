# companyApp/admin.py
from django import forms
from urllib.parse import urlparse, urlunparse

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.html import format_html

from .models import Company, CompanyContact, CompanyLink


# -------- permission helpers --------
def is_owner(u):
    return u.is_active and (u.is_superuser or u.groups.filter(name="Owner").exists())

def is_admin(u):
    return u.is_active and u.groups.filter(name="Admin").exists()

def is_hr(u):
    return u.is_active and u.groups.filter(name="HR").exists()

def is_plain_staff(u):
    return u.is_active and u.is_staff and not is_owner(u) and not is_admin(u) and not is_hr(u)


# -------- Inlines --------
class CompanyContactInline(admin.TabularInline):
    model = CompanyContact
    extra = 0
    autocomplete_fields = ["user"]
    fields = ("is_primary", "name", "title", "email", "phone", "notes", "user", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request, obj):
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


class CompanyLinkInline(admin.TabularInline):
    model = CompanyLink
    extra = 0
    fields = (
        "label", "url", "section", "visibility", "is_active", "sort_order",
        "tags", "key_name", "key_hint", "notes",
        "created_at", "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")

    def has_add_permission(self, request, obj):
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


# -------- Company form with "Use HTTPS" checkbox --------
class CompanyAdminForm(forms.ModelForm):
    use_https = forms.BooleanField(
        required=False,
        initial=True,
        label="Use HTTPS for Website",
        help_text="If checked, the website will be stored with https://; if unchecked, http://",
    )
    # CharField to allow inputs without scheme (e.g., 'example.com')
    website = forms.CharField(required=False, label="Website")

    class Meta:
        model = Company
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # initialize checkbox based on existing company website
        if self.instance and self.instance.pk and self.instance.website:
            self.fields["use_https"].initial = urlparse(self.instance.website).scheme == "https"

    def clean(self):
        cleaned = super().clean()
        raw = (cleaned.get("website") or "").strip()
        use_https = bool(cleaned.get("use_https"))

        if not raw:
            cleaned["website"] = ""
            return cleaned

        scheme = "https" if use_https else "http"
        p = urlparse(raw)

        if not p.scheme:
            # "example.com[/path]" -> add scheme
            netloc, sep, path = raw.partition("/")
            if path and not path.startswith("/"):
                path = "/" + path
            final = f"{scheme}://{netloc}{path}"
        else:
            # swap scheme, keep rest
            p = p._replace(scheme=scheme)
            final = urlunparse(p)

        try:
            URLValidator(schemes=["http", "https"])(final)
        except ValidationError as e:
            raise ValidationError({"website": e.messages})

        cleaned["website"] = final
        return cleaned


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    form = CompanyAdminForm

    list_display = (
        "logo_thumb",
        "name",
        "status",
        "pipeline_status",
        "city",
        "state_region",
        "website",
        "updated_at",
    )
    list_select_related = False
    list_filter = ("status", "pipeline_status", "country")
    search_fields = ("name", "primary_contact_name", "primary_email", "phone", "city", "state_region", "postal_code", "website")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CompanyContactInline, CompanyLinkInline]

    fieldsets = (
        ("Identity", {
            "fields": ("name", "slug", "status", "pipeline_status"),
        }),
        ("Logo", {
            "fields": ("logo", "logo_preview", "logo_external_url"),
        }),
        ("Contact", {
            "fields": ("primary_contact_name", "primary_email", "phone", "website", "use_https"),
        }),
        ("Address", {
            "fields": (
                "address_line1", "address_line2",
                "city", "state_region", "postal_code", "country",
            ),
        }),
        ("Consultation / CRM", {
            "fields": ("consultation_sheet_url", "first_contact_at", "last_contact_at", "notes"),
        }),
        ("Audit", {
            "fields": ("created_by", "created_at", "updated_at"),
        }),
    )
    readonly_fields = ("logo_preview", "created_at", "updated_at")

    # ----- logo preview -----
    def logo_preview(self, obj):
        if obj and (obj.logo or obj.logo_external_url):
            url = obj.logo.url if obj.logo else obj.logo_external_url
            return format_html('<img src="{}" style="height:48px;width:auto;object-fit:contain;border:1px solid #eee;padding:2px;background:#fff;" />', url)
        return "—"
    logo_preview.short_description = "Logo"

    def logo_thumb(self, obj):
        if obj and (obj.logo or obj.logo_external_url):
            url = obj.logo.url if obj.logo else obj.logo_external_url
            return format_html('<img src="{}" style="height:24px;width:auto;object-fit:contain;border:1px solid #eee;padding:1px;background:#fff;" />', url)
        return "—"
    logo_thumb.short_description = ""

    # ----- permissions -----
    def has_module_permission(self, request):
        if is_hr(request.user) or not request.user.is_staff:
            return False
        return True

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        # Only Owner/Admin can create Companies
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        # Owner/Admin can change; HR can change; plain staff read-only
        if is_owner(request.user) or is_admin(request.user):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        # Only Owner/Admin can delete Companies
        return is_owner(request.user) or is_admin(request.user)

    # Set created_by on first save
    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# -------- Standalone admins (optional if you want to manage outside the Company page) --------
@admin.register(CompanyContact)
class CompanyContactAdmin(admin.ModelAdmin):
    list_display = ("company", "is_primary", "name", "title", "email", "phone", "updated_at")
    list_filter = ("is_primary",)
    search_fields = ("company__name", "name", "email", "phone", "title")
    autocomplete_fields = ["company", "user"]
    readonly_fields = ("created_at", "updated_at")

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)


@admin.register(CompanyLink)
class CompanyLinkAdmin(admin.ModelAdmin):
    list_display = ("company", "label", "section", "visibility", "is_active", "sort_order", "updated_at")
    list_filter = ("visibility", "section", "is_active")
    search_fields = ("company__name", "label", "url", "tags", "notes")
    ordering = ("company__name", "sort_order", "label")
    autocomplete_fields = ["company", "created_by"]
    readonly_fields = ("created_at", "updated_at")

    fields = (
        "company",
        "label", "url", "section", "visibility", "is_active", "sort_order",
        "tags", "key_name", "key_hint", "notes",
        "created_by", "created_at", "updated_at",
    )

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return is_owner(request.user) or is_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_owner(request.user) or is_admin(request.user)
