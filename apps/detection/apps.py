from django.apps import AppConfig


class DetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Full dotted path keeps app resolution explicit in modular layouts.
    name = 'apps.detection'

    def ready(self):
        # Import signal handlers after app registry is loaded.
        from apps.detection import signals  # noqa: F401
