from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Full dotted path keeps app resolution explicit in modular layouts.
    name = 'apps.api'
