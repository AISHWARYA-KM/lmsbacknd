from django.apps import AppConfig


class LmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms'

    def ready(self):
        import lms.signals  # ✅ Must be imported so the signal runs


    
    
