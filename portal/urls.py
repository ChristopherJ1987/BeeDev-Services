from django.contrib import admin
from django.urls import path, include
from userApp import views as app_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('__reload__/', include('django_browser_reload.urls')),
    path('', include('userApp.urls')),
    path('admin/', admin.site.urls),
]
