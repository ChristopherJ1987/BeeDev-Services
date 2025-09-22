from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from ..models import ProposalDraft, DraftItem
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

@login_required
def view_draft_detail(request, pk: int):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    draft = (
        ProposalDraft.objects
        .select_related("company", "discount", "estimate_tier")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=DraftItem.objects
                    .select_related("job_rate", "base_setting", "catalog_item")
                    .order_by("sort_order", "pk"),
            )
        )
        .get(pk=pk)
    )
    theList = list(draft.items.all())
    title = f"{draft.title} Proposal Draft"
    ctx = {"user_obj": user, "read_only": True, "draft": draft, "items": list(draft.items.all())}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "proposal_staff/view_draft_detail.html", ctx)