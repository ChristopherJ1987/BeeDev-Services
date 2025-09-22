# core/admin.py
from django.contrib import admin
from .models import Announcement, Version

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("slug", "audience", "severity", "priority", "is_active", "starts_at", "ends_at", "updated_at")
    list_filter  = ("audience", "severity", "is_active")
    search_fields = ("slug", "title", "message_html")
    ordering = ("priority",)

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("slug", "version_num", "info", "date_of_release", "updated_at")
    list_filter = ("version_num", "date_of_release")
    ordering = ("date_of_release",)