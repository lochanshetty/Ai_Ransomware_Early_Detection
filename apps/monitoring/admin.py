from django.contrib import admin

from apps.monitoring.models import ProtectedFile


@admin.register(ProtectedFile)
class ProtectedFileAdmin(admin.ModelAdmin):
    list_display = ("file_path", "file_type", "added_at")
    search_fields = ("file_path", "file_type")
