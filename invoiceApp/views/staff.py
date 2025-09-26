from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from core.utils.context import base_ctx
from ..models import Invoice

@login_required
def invoice_home(request):
    user = request.user
    allowed_roles = {user.Roles.ADMIN, user.Roles.OWNER}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    invoices = Invoice.objects.all()
    unpaid = Invoice.objects.exclude(status__in=["PAID"])
    paid = Invoice.objects.filter(status="PAID")

    title = "Invoice Admin"
    ctx = {"user_obj": user, "read_only": True, "invoices": invoices, "unpaid": unpaid, "paid": paid}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "invoice_staff/invoice_home.html", ctx)