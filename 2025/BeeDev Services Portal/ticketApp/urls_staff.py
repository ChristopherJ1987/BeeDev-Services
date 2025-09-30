from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base/tickets/

app_name = "ticket_staff"

urlpatterns = [
    # path('', views.ticket_admin, name='ticket_admin'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)