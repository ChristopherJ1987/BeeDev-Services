from django.urls import path, reverse_lazy
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

# All urls are at base /

app_name = "proposal_staff"

urlpatterns = [
    path('', views.proposal_home, name='proposal_home'),
    path('/all', views.view_all_drafts, name='view_all_drafts'),
    path('<int:pk>/', views.view_draft_detail, name='detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)