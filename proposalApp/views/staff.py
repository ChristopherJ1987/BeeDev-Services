from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from ..models import ProposalDraft
from core.utils.context import base_ctx

@login_required
def view_all_drafts(request):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    drafts = ProposalDraft.objects.all()

    title = "Proposal Drafts"
    ctx = {"user_obj": user, "read_only": True, "drafts": drafts}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "proposal_staff/view_all_drafts.html", ctx)