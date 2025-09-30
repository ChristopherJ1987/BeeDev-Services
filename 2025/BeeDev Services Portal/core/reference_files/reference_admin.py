from django.contrib import admin
from userApp.admin_mixins import HideFromHRMixin
from .models import Proposal, ProposalItem

@admin.register(Proposal)
class ProposalAdmin(HideFromHRMixin, admin.ModelAdmin):
    list_display = ("title", "recipient_email", "status", "created_by", "created_at")
    # ... your existing config ...

@admin.register(ProposalItem)
class ProposalItemAdmin(HideFromHRMixin, admin.ModelAdmin):
    # ... config ...
    pass
