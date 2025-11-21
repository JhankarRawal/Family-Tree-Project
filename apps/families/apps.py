from django.apps import AppConfig

class FamiliesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.families'
    label = 'families' # Added label to avoid conflicts


    def ready(self):
        # import signal handlers
        import apps.families.signals  # noqa: F401
