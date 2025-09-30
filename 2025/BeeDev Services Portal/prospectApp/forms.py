from django import forms
from .models import Prospect

class ProspectForm(forms.ModelForm):
    class Meta:
        model = Prospect
        # Adjust this list to your model’s real fields
        fields = [
            "full_name", "email", "phone",
            "company_name", "status", "notes"
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        return email.lower()
