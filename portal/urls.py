from django.contrib import admin
from django.urls import path, include, reverse_lazy
from userApp import views as app_views
from companyApp import views as app_views
from proposalApp import views as app_views
from ticketApp import views as app_views
from prospectApp import views as app_views
from projectApp import views as app_views
from invoiceApp import views as app_views
from django.contrib.auth import views as auth_views

handler403 = "core.views.custom_permission_denied_view"

admin.site.site_header = "BeeDev Admin"
admin.site.site_title = "BeeDev Admin"
admin.site.index_title = "BeeDev Administration"

admin.site.site_url = reverse_lazy("userApp:employee_home")

urlpatterns = [
    path('__reload__/', include('django_browser_reload.urls')),
    path('', include('userApp.urls')),
    path('admin/', admin.site.urls),
    # Staff
    path('companies/', include(('companyApp.urls_staff', 'company_staff'), namespace='company_staff')),
    path('proposals/', include(('proposalApp.urls_staff', 'proposal_staff'), namespace='proposals_staff')),
    path('projects/', include(('projectApp.urls_staff', 'projects_staff'), namespace='projects_staff')),
    path('invoices/', include(('invoiceApp.urls_staff', 'invoice_staff'), namespace='invoice_staff')),
    path('tickets/', include(('ticketApp.urls_staff', 'ticket_staff'), namespace='ticket_staff')),
    path('prospects/', include(('prospectApp.urls', 'prospects'), namespace='prospects')),
    # Client
    path('client/company/', include(('companyApp.urls_client', 'company_client'), 
    namespace='company_client')),
    path('client/proposals/', include(('proposalApp.urls_client', 'proposal_client'), namespace='proposal_client')),
    path('client/invoices/', include(('invoiceApp.urls_client', 'invoice_client'), namespace='invoice_client')),
    path('client/projects/', include(('projectApp.urls_client', 'project_client'), namespace='project_client')),
    path('client/tickets/', include(('ticketApp.urls_client', 'ticket_client'), namespace='ticket_client')),
]
