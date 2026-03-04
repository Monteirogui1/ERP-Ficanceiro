from django.apps import AppConfig


class BancarioConfig(AppConfig):
    name = 'apps.bancario'

    def ready(self):
        import apps.bancario.signals