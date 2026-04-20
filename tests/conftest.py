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
            "WAVE": {"API_KEY": "test-key", "SANDBOX": True},
            "ORANGE_MONEY": {"CLIENT_ID": "test-id", "CLIENT_SECRET": "test-secret"},
            "MTN_MOMO": {"SUBSCRIPTION_KEY": "test-key", "ENVIRONMENT": "sandbox"},
            "MOOV_MONEY": {"USERNAME": "test", "PASSWORD": "test", "PARTNER_ID": "test", "SANDBOX": True},
            "AIRTEL_MONEY": {"CLIENT_ID": "test-id", "CLIENT_SECRET": "test-secret", "COUNTRY": "CI", "SANDBOX": True},
            "FREE_MONEY": {"API_KEY": "test-key", "MERCHANT_ID": "test-merchant", "SANDBOX": True},
            "MPESA": {"CONSUMER_KEY": "test-key", "CONSUMER_SECRET": "test-secret", "SHORTCODE": "123456", "PASSKEY": "test-pass", "SANDBOX": True},
            "WIZALL_MONEY": {"API_KEY": "test-key", "MERCHANT_ID": "test-merchant", "SANDBOX": True},
            "CELTIIS_CASH": {"API_KEY": "test-key", "MERCHANT_ID": "test-merchant", "COUNTRY": "BJ", "SANDBOX": True},
            "YAS_MONEY": {"API_KEY": "test-key", "MERCHANT_ID": "test-merchant", "SANDBOX": True},
            "CINETPAY":   {"API_KEY": "test-key", "SITE_ID": "test-site", "SANDBOX": True},
            "SAMA_MONEY": {"API_KEY": "test-key", "MERCHANT_ID": "test-merchant", "SANDBOX": True},
            "ECOBANK":    {"CLIENT_ID": "test-id", "CLIENT_SECRET": "test-secret", "MERCHANT_ID": "test-merchant", "COUNTRY": "CI", "SANDBOX": True},
        },
    )