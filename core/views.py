# core/views.py
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from core.utils.context import base_ctx

def custom_permission_denied_view(request, exception=None):
    # You can differentiate messages here, e.g. by exception args/class
    title = "Access denied"
    ctx = {
        "page_heading": title,
        "reason": getattr(exception, "args", [None])[0],  # e.g., "Not allowed"
        "user_role": getattr(request.user, "role", None),
        "requested_path": request.path,
    }
    ctx.update(base_ctx(request, title=title))
    return render(request, "errors/403.html", ctx, status=403)
