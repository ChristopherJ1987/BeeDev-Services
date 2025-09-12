from django.urls import path, reverse_lazy
# from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

# All urls are at base /

app_name = "userApp"

urlpatterns = [
    path("", PortalLogin.as_view(), name="login"),
    path("post-login/", post_login, name="post_login"),
    path("staff/", staff_home, name="staff_home"),
    path("client/", client_home, name="client_home"),
    path("employee/", employee_home, name="employee_home"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)