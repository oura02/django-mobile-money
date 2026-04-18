import django
from django.conf import settings


def pytest_configure():
    settings.configure(
        SECRET_KEY="django-mobile-money-test-secret-key",
        DEBUG=True,
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_mobile_money",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        MOBILE_MONEY={
            "DEFAULT_BACKEND": "wave",
            "WAVE": {
                "API_KEY": "test-api-key",
                "SANDBOX": True,
            },
            "ORANGE_MONEY": {
                "CLIENT_ID": "test-client-id",
                "CLIENT_SECRET": "test-secret",
                "SANDBOX": True,
            },
            "MTN_MOMO": {
                "SUBSCRIPTION_KEY": "test-sub-key",
                "ENVIRONMENT": "sandbox",
            },
            "MOOV_MONEY": {
                "USERNAME": "test-user",
                "PASSWORD": "test-pass",
                "PARTNER_ID": "test-partner",
                "SANDBOX": True,
            },
        },
    )