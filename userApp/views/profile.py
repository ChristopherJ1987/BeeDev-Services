from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from ..models import ClientProfile, EmployeeProfile
from core.utils.context import base_ctx

@login_required
def view_client_profile(request):
    user = request.user
    if getattr(user, 'role', None) != user.Roles.CLIENT:
        raise PermissionDenied("This page is for clients only")
    profile, _ = ClientProfile.objects.get_or_create(user=user)
    title = f"{user.preferred_name} Profile"
    ctx = {
        "user_obj": user,
        "profile": profile,
    }

    print(user)
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title

    return render(request, "userApp/view_client_profile.html", ctx)

@login_required
def view_employee_profile(request):
    user = request.user
    allowed_roles = {user.Roles.EMPLOYEE, user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, "role", None) not in allowed_roles:
        raise PermissionDenied("Not allowed")

    # Only create profile for actual EMPLOYEEs
    if user.role == user.Roles.EMPLOYEE:
        profile, _ = EmployeeProfile.objects.get_or_create(user=user)
    else:
        profile = getattr(user, "employee_profile", None)
        if not profile:
            raise PermissionDenied("No employee profile found")

    title = f"{user.preferred_name} Profile"
    ctx = {"user_obj": user, "profile": profile, "read_only": True}
    ctx.update(base_ctx(request, title=title))
    ctx["page_heading"] = title
    return render(request, "userApp/view_employee_profile.html", ctx)
