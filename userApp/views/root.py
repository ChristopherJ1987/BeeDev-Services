from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

class PortalLogin(LoginView):
    template_name = "userApp/index.html"
    redirect_authenticated_user = True

    # You can add your custom context just like your index() example:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx = {"title": "Portal"}
        return ctx

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
        "title": "Dashboard - BeeDev Services",
        "user_name": u.get_full_name() or u.username,
    }
    return render(request, "userApp/client_home.html", ctx)