from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from ..models import ClientProfile
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