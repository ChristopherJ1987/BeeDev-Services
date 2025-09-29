from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base/prospects/

app_name = "prospects"

urlpatterns = [
    path('new', views.add_prospect, name="add_prospect"),
    path('<int:pk>', views.view_prospect, name="view_one_prospect"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)