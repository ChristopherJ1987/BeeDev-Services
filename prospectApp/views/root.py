from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from core.utils.context import base_ctx
from ..forms import ProspectForm
from ..models import Prospect

@login_required
def add_prospect(request):
    user = request.user
    # match your existing role-gate style
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")

    if request.method == "POST":
        form = ProspectForm(request.POST)
        if form.is_valid():
            prospect = form.save(commit=False)
            # if your model has these fields, they’ll set; otherwise remove
            if hasattr(prospect, "created_by"):
                prospect.created_by = user
            prospect.save()
            messages.success(request, "Prospect added successfully.")
            # send them somewhere useful; adjust as needed
            if Prospect._meta.get_field("id"):
                return redirect("prospectApp:detail", pk=prospect.pk)
            return redirect("prospectApp:list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProspectForm()

    title = "Add Prospect"
    ctx = {"form": form}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "prospectApp/prospect_form.html", ctx)