from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base /

app_name = "company_staff"

urlpatterns = [
    path('', views.view_all_companies, name='view_all_companies'),
    path('<int:pk>/', views.view_one, name='detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)