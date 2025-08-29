from django.contrib.auth.forms import AuthenticationForm

class PortalAuthForm(AuthenticationForm):
    """
    Same fields as the default login form, but with placeholders/classes.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Username",
            "class": "input",
            "autocomplete": "username",
            "aria-label": "Username",
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": "Password",
            "class": "input",
            "autocomplete": "current-password",
            "aria-label": "Password",
        })