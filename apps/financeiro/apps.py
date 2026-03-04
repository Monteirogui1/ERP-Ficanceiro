from django.apps import AppConfig


class FinanceiroConfig(AppConfig):
    name = 'apps.financeiro'

    def ready(self):
        import apps.financeiro.signals