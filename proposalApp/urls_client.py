from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base/client/proposals/

app_name = "proposal_client"

urlpatterns = [
    path('', views.view_all_client_proposals, name='view_all_client_proposals'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)