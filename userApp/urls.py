from django.urls import path, reverse_lazy
# from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

# All urls are at base /

app_name = "userApp"

urlpatterns = [
    #  || General Links ||
    path("", PortalLogin.as_view(), name="login"),
    path("post-login/", post_login, name="post_login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # || Staff/Employee Links ||
    path("staff/", staff_home, name="staff_home"),
    path("staff/list", view_all_staff, name="view_all_staff"),
    path("employee/", employee_home, name="employee_home"),
    path("employee/profile", view_employee_profile, name="view_employee_profile"),

    # || Client Links ||
    path("client/", client_home, name="client_home"),
    path("client/profile", view_client_profile, name="view_client_profile"),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)