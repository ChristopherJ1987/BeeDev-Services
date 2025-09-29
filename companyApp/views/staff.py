from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404, redirect
from ..models import Company, CompanyContact, CompanyLink
from ..forms import CompanyForm
from prospectApp.models import Prospect
from proposalApp.models import ProposalDraft, DraftItem, Proposal, ProposalEvent
from core.utils.context import base_ctx
from django.core.paginator import Paginator
from django.db.models import Prefetch, Count, Sum, Q
from django.contrib import messages

@login_required
def company_home(request):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    companies = Company.objects.all()
    prospects = Prospect.objects.all()

    title = "Company Admin"
    ctx = {"user_obj": user, "read_only": True, "companies": companies, "prospects": prospects}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "company_staff/company_home.html", ctx)

@login_required
def view_all_companies(request):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    q = (request.GET.get("q") or "").strip()
    companies = Company.objects.all()
    if q:
        companies = companies.filter(name__icontains=q)

    companies = companies.order_by("name")
    paginator = Paginator(companies, 50)
    page_obj = paginator.get_page(request.GET.get("page"))
    
    title = "Company List"
    ctx = {"user_obj": user, "read_only": True, "page_obj": page_obj}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "company_staff/view_all.html", ctx)

@login_required
def view_company_detail(request, pk: int):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    company = get_object_or_404(Company, pk=pk)
    contacts = CompanyContact.objects.filter(company=company).order_by("name")
    links = CompanyLink.objects.filter(company=company).order_by("id")

    drafts = (company.pricing_drafts.select_related("discount", "estimate_tier", "created_by").prefetch_related(Prefetch("items", queryset=DraftItem.objects.select_related("job_rate","base_setting","catalog_item").order_by("sort_order","pk"))).order_by("-updated_at"))

    proposals = (company.simple_proposals.select_related("created_by").prefetch_related("line_items", "applied_discounts", "recipients", "events").order_by("created_at"))

    proposal_stats = proposals.aggregate(count=Count("id"), signed=Count("id", filter=Q(signed_at__isnull=False)), pending=Count("id", filter=Q(signed_at__isnull=True)), total_amount=Sum("amount_total"))

    recent_events = (ProposalEvent.objects.filter(proposal__company=company).select_related("proposal", "actor").order_by("-at")[:10])

    title = f"{company.name} - Details"
    ctx = {"user_obj": user, "read_only": True, "company": company, "contacts":contacts, "links": links, "drafts": drafts, "proposals": proposals, "proposal_stats": proposal_stats, "recent_events": recent_events}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "company_staff/view_company_detail.html", ctx)

@login_required
def add_company(request):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            if hasattr(company, "created_by"):
                company.created_by = user
            company.save()
            messages.success(request, "Company added successfully.")

            return redirect("company_staff:company_home")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CompanyForm()
    title = "Add Company"
    ctx = {"form": form}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "company_staff/add_company_form.html", ctx)