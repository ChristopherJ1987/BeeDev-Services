from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base/client/tickets/

app_name = "ticket_client"

urlpatterns = [
    # path('', views.view_all_client_tickets, name='view_all_client_tickets'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)