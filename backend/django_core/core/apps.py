from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Research Platform'
    
    def ready(self):
        """Import signal handlers when the app is ready."""
        try:
            import core.signals
        except ImportError:
            pass  # Signals are optional
