from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from ..models import Proposal, ProposalLineItem
from core.utils.context import base_ctx

@login_required
def view_all_client_proposals(request):
    user = request.user
    allowed_roles = {user.Roles.CLIENT}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    title = "Proposals"
    ctx = {"user_obj": user, "read_only": True}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "proposal_client/view_all_proposals.html", ctx)