from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Prefetch, Max
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from ..models import ProposalDraft, DraftItem, Proposal, ProposalLineItem, ProposalAppliedDiscount, ProposalRecipient, ProposalEvent
from userApp.models import User
from core.utils.context import base_ctx
from django.contrib import messages
from django.urls import reverse

def _is_owner(user):
    return user.is_active and (user.is_superuser or user.role == User.Roles.OWNER)

def _is_admin(user):
    return user.is_active and user.role == User.Roles.ADMIN

def _is_employee(user):
    return user.is_active and (user.role in [User.Roles.EMPLOYEE, User.Roles.ADMIN, User.Roles.OWNER])

@login_required
def proposal_home(request):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    drafts = ProposalDraft.objects.exclude(approval_status='CONVERTED')

    proposals_qs = (
        Proposal.objects
        .select_related("company")
        .annotate(last_event_at=Max("events__at"))
        .prefetch_related(
            Prefetch(
                "events",
                queryset=ProposalEvent.objects.select_related("actor").order_by("-at", "pk")
            )
        )
        .order_by("-last_event_at", "-created_at")
    )
    proposals = list(proposals_qs)
    last_events_by_id = {
        p.id: (p.events.all()[0] if p.events.all() else None)
        for p in proposals
    }
    print(proposals, last_events_by_id)
    title = "Proposal Admin"
    ctx = {"user_obj": user, "read_only": True, "drafts": drafts, "proposals": proposals, "last_events_by_id": last_events_by_id}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "proposal_staff/proposal_home.html", ctx)

@login_required
def view_draft_detail(request, pk: int):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER}
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
        .filter(pk=pk)
        .first()
    )
    if not draft:
        raise PermissionDenied("Draft not found")
    
    admin_users = User.objects.filter(is_active=True, role__in=[User.Roles.ADMIN, User.Roles.OWNER]).order_by("first_name", "last_name", "username")

    if request.method == "POST":
        action = request.POST.get("action")

        # 1) Submit for approval
        if action == "submit":
            reviewer_id = request.POST.get("reviewer_id")
            if reviewer_id and hasattr(draft, "assigned_reviewer_id"):
                try:
                    draft.assigned_reviewer_id = int(reviewer_id)
                    draft.save(update_fields=["assigned_reviewer_id"])
                except Exception:
                    pass
            
            try:
                draft.mark_submitted(actor=user, save=True)
            except ValidationError as e:
                messages.error(
                    request, "Cannot submit: the company is missing a primary email."
                    "Add it to the Company and try again."
                )
                return redirect(request.path)
            messages.success(request, "Draft submitted for approval.")
            return redirect(request.path)

        # 2) Approve / Reject (Admin/Owner only)
        if action in {"approve", "reject"}:
            if not (user.role in (User.Roles.ADMIN, User.Roles.OWNER) or user.is_superuser):
                raise PermissionDenied("Only Admin/Owner may approve or reject drafts.")
            notes = (request.POST.get("approval_notes") or "").strip()
            if action == "approve":
                draft.mark_approved(actor=user, notes=notes, save=True)
                messages.success(request, "Draft approved.")
            else:
                draft.mark_rejected(actor=user, notes=notes, save=True)
                messages.info(request, "Draft rejected.")
            return redirect(request.path)

        # 3) Convert to Proposal (only after Approved)
        if action == "convert":
            if draft.approval_status != ProposalDraft.ApprovalStatus.APPROVED:
                messages.error(request, "Draft must be approved before conversion.")
                return redirect(request.path)
            with transaction.atomic():
                proposal = draft.convert_to_proposal(actor=user)
            messages.success(request, "Converted to proposal.")
            return redirect(reverse("proposal_staff:proposal_detail", args=[proposal.id]))

        messages.error(request, "Unknown action.")
        return redirect(request.path)

    
    theList = list(draft.items.all())
    title = f"{draft.title} Proposal Draft"
    ctx = {"user_obj": user, "read_only": True, "draft": draft, "items": theList, "admin_users": admin_users, "can_approve": (user.role in (User.Roles.ADMIN, User.Roles.OWNER) or user.is_superuser)}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "proposal_staff/view_draft_detail.html", ctx)

@login_required
def view_proposal_detail(request, pk: int):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    proposal = (
        Proposal.objects
        .select_related("company", "created_by", "approver_user")
        .prefetch_related(
            Prefetch(
                "line_items",
                queryset=ProposalLineItem.objects
                    .select_related("job_rate", "base_setting")
                    .order_by("sort_order", "pk"),
            ),
            Prefetch(
                "applied_discounts",
                queryset=ProposalAppliedDiscount.objects.order_by("sort_order", "id")
            ),
            Prefetch(
                "recipients",
                queryset=ProposalRecipient.objects.order_by("-is_primary", "email")
            ),
            Prefetch(
                "events",
                queryset=ProposalEvent.objects.select_related("actor").order_by("-at", "pk")
            )
        )
        .get(pk=pk)
    )
    theList = list(proposal.line_items.all())
    events = list(proposal.events.all())

    title = f"{proposal.title} Proposal"
    ctx = {"user_obj": user, "read_only": True, "proposal": proposal, "items": theList, "events": events}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title 
    return render(request, "proposal_staff/view_proposal_detail.html", ctx)