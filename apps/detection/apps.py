from django.apps import AppConfig


class DetectionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # Full dotted path keeps app resolution explicit in modular layouts.
    name = 'apps.detection'

    def ready(self):
        from apps.detection import signals  # noqa: F401
        from apps.detection.services.model_loader import model_loader

        if not model_loader.is_ready:
            loaded = model_loader.reload()
            if not loaded:
                try:
                    from training.train import train_model
                    train_model(model_type="random_forest", output_name="random_forest_v1")
                    model_loader.reload("random_forest_v1")
                except Exception:  # noqa: BLE001
                    import logging
                    logging.getLogger(__name__).warning(
                        "Could not auto-train model on startup; run: python training/train.py"
                    )
