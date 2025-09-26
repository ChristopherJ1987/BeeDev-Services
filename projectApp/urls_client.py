from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base/client/projects

app_name = "project_client"

urlpatterns = [
    # path('', views.view_all_client_projects, name='view_all_client_projects'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)