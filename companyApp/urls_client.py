from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base /

app_name = "company_client"

urlpatterns = [
    # path('', views.ClientCompanyHomeView.as_view(), name='home'),
    # path('profile/', views.ClientCompanyProfileView.as_view(), name='profile'),
    # path('<int:pk>/', views.ClientCompanyDetailView.as_view(), name='detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)