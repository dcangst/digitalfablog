from django.apps import AppConfig


class CashierConfig(AppConfig):
    name = 'cashier'

    def ready(self):
        import cashier.signals
