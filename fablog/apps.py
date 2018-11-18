from django.apps import AppConfig


class FablogConfig(AppConfig):
    name = 'fablog'

    def ready(self):
        import fablog.signals
