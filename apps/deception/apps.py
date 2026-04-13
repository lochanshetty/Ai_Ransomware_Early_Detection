from django.apps import AppConfig


class DeceptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Full dotted path keeps app resolution explicit in modular layouts.
    name = 'apps.deception'

    def ready(self):
        # Register deception signal handlers at app startup.
        from apps.deception import signals  # noqa: F401
