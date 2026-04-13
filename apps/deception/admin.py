from django.contrib import admin

from apps.deception.models import HoneypotAccessEvent, HoneypotFile


@admin.register(HoneypotFile)
class HoneypotFileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "file_path", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("display_name", "file_path")


@admin.register(HoneypotAccessEvent)
class HoneypotAccessEventAdmin(admin.ModelAdmin):
    list_display = ("honeypot_file", "process_name", "detected_at")
    search_fields = ("process_name", "honeypot_file__file_path")
