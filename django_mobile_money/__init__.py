default_app_config = "django_mobile_money.apps.DjangoMobileMoneyConfig"


def pay(phone: str, amount, backend: str = None, **kwargs) -> dict:
    from django.conf import settings
    from .backends import BACKENDS

    backend_id = backend or settings.MOBILE_MONEY.get("DEFAULT_BACKEND", "wave")

    BackendClass = BACKENDS.get(backend_id)
    if not BackendClass:
        raise ValueError(
            f"Backend '{backend_id}' introuvable. "
            f"Choix disponibles : {list(BACKENDS.keys())}"
        )

    return BackendClass().initiate_payment(
        phone=phone,
        amount=amount,
        **kwargs,
    )