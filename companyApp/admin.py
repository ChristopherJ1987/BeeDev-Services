# companyApp/admin.py
from django import forms
from urllib.parse import urlparse, urlunparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.contrib import admin
from .models import Company

class CompanyAdminForm(forms.ModelForm):
    # UI-only checkbox to choose the scheme
    use_https = forms.BooleanField(
        required=False, initial=True, label="Use HTTPS",
        help_text="If checked, the website will be stored with https://; if unchecked, http://"
    )
    # Allow inputs without scheme like "example.com"
    website = forms.CharField(required=False, label="Website")

    class Meta:
        model = Company
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
            # "example.com[/path]" → add scheme
            netloc, sep, path = raw.partition("/")
            if path and not path.startswith("/"):
                path = "/" + path
            final = f"{scheme}://{netloc}{path}"
        else:
            # Swap scheme, keep host/path/query/fragment
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
    list_display = ("name", "status", "city", "state_region", "phone", "website", "updated_at")
    search_fields = ("name", "primary_email", "phone", "city", "state_region", "postal_code", "website")
    list_filter = ("status", "country")
    prepopulated_fields = {"slug": ("name",)}
