from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from ..models import User, ClientProfile, EmployeeProfile
from prospectApp.models import Prospect
from core.utils.context import base_ctx

@login_required
def view_all_staff(request):
    user = request.user
    allowed_roles = {user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, 'role', None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    staff = User.objects.filter(is_staff=True)
    title = 'Team Admin'
    ctx = {"user_obj": user, "staff": staff}
    ctx.update(base_ctx(request, title=title))
    ctx['page_heading'] = title
    return render(request, "userApp/staff/view_all_staff.html", ctx)

@login_required
def view_staff_profile(request, pk: int):
    user = request.user
    allowed_roles = {user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, 'role', None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    staff = get_object_or_404(User, pk=pk)
    profile = get_object_or_404(EmployeeProfile, user=staff)
    title = f"{staff.preferred_name}'s Profile"
    ctx = {"user_obj": user, "staff": staff, "profile": profile}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "userApp/staff/view_staff_profile.html", ctx)

@login_required
def view_all_clients(request):
    user = request.user
    allowed_roles = {user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, 'role', None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    contacts = User.objects.filter(is_staff=False)
    prospects = Prospect.objects.exclude(status__in=["WON", "LOST", "UNSUB"])
    title = 'Contacts Admin'
    ctx = {"user_obj": user, "contacts": contacts, "prospects": prospects}
    ctx.update(base_ctx(request, title=title))
    ctx['page_heading'] = title
    return render(request, "userApp/staff/view_all_contacts.html", ctx)