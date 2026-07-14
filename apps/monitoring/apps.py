from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitoring'

    def ready(self):
        from django.conf import settings

        if getattr(settings, 'CRDS_AUTO_START_MONITORING', False):
            from apps.monitoring.services import monitor_runtime
            try:
                monitor_runtime.start()
            except Exception:  # noqa: BLE001
                import logging
                logging.getLogger(__name__).warning("Auto-start monitoring failed")
