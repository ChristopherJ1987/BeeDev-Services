from django.apps import AppConfig


class UserappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userApp'

    def ready(self):
        from . import signals  # registers signal handlers