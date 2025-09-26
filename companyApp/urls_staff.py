from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base/companies/

app_name = "company_staff"

urlpatterns = [
    path('', views.company_home, name="company_home"),
    path('company/<int:pk>/', views.view_company_detail, name='company_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)