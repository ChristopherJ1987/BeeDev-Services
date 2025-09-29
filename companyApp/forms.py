from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            "name", "primary_contact_name", "primary_email", "phone", "website", "status", "pipeline_status", "notes"
        ]
        labels = {
            "name": "Company Name"
        }
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
            "name": forms.TextInput(attrs={"placeholder": "e.g., Acme Corp"}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get("primary_email", "").strip()
        return email.lower()