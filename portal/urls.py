from django.contrib import admin
from django.urls import path, include, reverse_lazy
from userApp import views as app_views
from django.contrib.auth import views as auth_views

admin.site.site_header = "BeeDev Admin"
admin.site.site_title = "BeeDev Admin"
admin.site.index_title = "BeeDev Administration"

admin.site.site_url = reverse_lazy("userApp:employee_home")

urlpatterns = [
    path('__reload__/', include('django_browser_reload.urls')),
    path('', include('userApp.urls')),
    path('admin/', admin.site.urls),
]
