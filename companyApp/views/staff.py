from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from ..models import Company, CompanyContact, CompanyLink
from core.utils.context import base_ctx
from django.core.paginator import Paginator

@login_required
def view_all_companies(request):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
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
def view_one(request, pk: int):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    company = get_object_or_404(Company, pk=pk)
    contacts = CompanyContact.objects.filter(company=company).order_by("name")
    links = CompanyLink.objects.filter(company=company).order_by("id")

    title = f"{company.name} - Details"
    ctx = {"user_obj": user, "read_only": True, "company": company, "contacts":contacts, "links": links}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "company_staff/view_detail.html", ctx)