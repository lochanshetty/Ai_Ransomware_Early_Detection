from django.contrib import admin

from apps.deception.models import HoneypotFile


@admin.register(HoneypotFile)
class HoneypotFileAdmin(admin.ModelAdmin):
    list_display = ("file_path", "is_triggered", "created_at")
    list_filter = ("is_triggered",)
    search_fields = ("file_path",)
