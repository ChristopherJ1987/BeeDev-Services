from django.urls import path
# from . import views
from .views import PortalLogin, post_login, staff_home, client_home
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base /

app_name = "userApp"

urlpatterns = [
    path("", PortalLogin.as_view(), name="login"),
    path("post-login/", post_login, name="post_login"),
    path("staff/", staff_home, name="staff_home"),
    path("client/", client_home, name="client_home"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)