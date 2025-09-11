from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.utils.context import CommonContextMixin, base_ctx
from ..forms import PortalAuthForm

class PortalLogin(CommonContextMixin,LoginView):
    template_name = "userApp/index.html"
    redirect_authenticated_user = True
    form_class = PortalAuthForm
    common_title = "Portal"


@login_required
def post_login(request):
    u = request.user
    if getattr(u, "is_staff", False) or getattr(u, "role", None) == "EMPLOYEE":
        return redirect("admin:index")

    # Otherwise go to client dashboard
    return redirect("userApp:client_home")

@login_required
def staff_home(request):
    return redirect("admin:index")

@login_required
def client_home(request):
    u = request.user
    ctx = {
        "user_name": u.get_full_name() or u.username,
    }
    ctx.update(base_ctx(request, title="Dashboard"))
    return render(request, "userApp/client_home.html", ctx)