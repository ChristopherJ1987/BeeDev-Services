from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from ..models import User, ClientProfile, EmployeeProfile
from core.utils.context import base_ctx

@login_required
def view_all_staff(request):
    user = request.user
    allowed_roles = {user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, 'role', None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    staff = User.objects.all()
    print('staff', staff)
    title = 'Staff List'
    ctx = {"user_obj": user, "staff": staff}
    ctx.update(base_ctx(request, title=title))
    ctx['page_heading'] = title
    return render(request, "userApp/view_all_staff.html", ctx)

@login_required
def view_staff_profile(request, pk: int):
    user = request.user
    allowed_roles = {user.Roles.ADMIN, user.Roles.OWNER, user.Roles.HR}
    if getattr(user, 'role', None) not in allowed_roles:
        raise PermissionDenied("Not allowed")
    
    staff = get_object_or_404(User, pk=pk)
    pass