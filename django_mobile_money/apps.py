from django.apps import AppConfig


class DjangoMobileMoneyConfig(AppConfig):
    name = "django_mobile_money"
    verbose_name = "Mobile Money"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import django_mobile_money.signals  # noqa: F401