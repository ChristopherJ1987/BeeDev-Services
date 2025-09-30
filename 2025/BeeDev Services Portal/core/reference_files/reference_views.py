"""
Reference views for BeeDev Portal.
Copy-paste into any app and tweak. Do not include in urls directly.

IMPORT CHEAT SHEET:
───────────────────────────────
If your app has a flat structure:
    userApp/
      views.py
      forms.py
      models.py

    → use:
        from .forms import SomeForm
        from .models import SomeModel

If your app has a foldered views structure:
    userApp/
      views/
        __init__.py
        root.py
      forms.py
      models.py

    → use:
        from ..forms import SomeForm
        from ..models import SomeModel
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import TemplateView

# Always safe (project-wide helpers live in core/)
from core.utils.context import base_ctx, CommonContextMixin


# ──────────────────────────────────────────────────────────────
# FBV (Function-Based View) TEMPLATE
# ──────────────────────────────────────────────────────────────
@login_required
def reference_fbv(request):
    """
    Template FBV:
    - Put view-specific data in ctx
    - Add shared bits with base_ctx()
    - base_ctx("Dashboard") → "Dashboard - BeeDev Services"
    """
    ctx = {
        # view-specific data goes here
        "example_list": ["alpha", "bravo", "charlie"],
    }
    ctx.update(base_ctx(request, title="Sample Page"))
    # Page body heading → "Active Sample"
    ctx["page_heading"] = "Active Sample"
    return render(request, "reference/fbv_sample.html", ctx)


# ──────────────────────────────────────────────────────────────
# CBV (Class-Based View) TEMPLATE
# ──────────────────────────────────────────────────────────────
class ReferenceCBV(CommonContextMixin, TemplateView):
    """
    Template CBV:
    - Extend a generic view (TemplateView/DetailView/ListView/etc.)
    - CommonContextMixin adds base_ctx(request, title=common_title)
    """
    template_name = "reference/cbv_sample.html"
    common_title = "Sample Page"  # becomes "Sample Page - BeeDev Services"

    # If you need extra context beyond base_ctx, you can still extend:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)  # includes base_ctx via mixin
        ctx["extra"] = "value"
        # Page body heading → "Active Sample"
        ctx["page_heading"] = "Active Sample"
        return ctx
