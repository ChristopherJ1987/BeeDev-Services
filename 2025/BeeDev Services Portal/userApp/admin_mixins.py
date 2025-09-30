from django.contrib import admin

def is_hr(user):
    return user.is_active and user.groups.filter(name="HR").exists()

class HideFromHRMixin:
    """Apply to ModelAdmin classes to hide the entire model/app from HR users."""
    def has_module_permission(self, request):
        if is_hr(request.user):
            return False
        return super().has_module_permission(request)

    def get_model_perms(self, request):
        if is_hr(request.user):
            # Returning {} removes the model from the app index for that user
            return {}
        return super().get_model_perms(request)
