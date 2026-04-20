# django-mobile-money

[![PyPI version](https://badge.fury.io/py/django-mobile-money.svg)](https://badge.fury.io/py/django-mobile-money)
[![Tests](https://github.com/oura02/django-mobile-money/actions/workflows/tests.yml/badge.svg)](https://github.com/oura02/django-mobile-money/actions)
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)](https://github.com/oura02/django-mobile-money)
[![Python](https://img.shields.io/pypi/pyversions/django-mobile-money)](https://pypi.org/project/django-mobile-money/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/django-mobile-money)](https://pypi.org/project/django-mobile-money/)

> Package Django reusable pour les paiements Mobile Money africains.
> Integrez Wave, Orange Money, MTN MoMo et Moov Money en 3 lignes de code.

## Backends supportes

| Provider     | Pays                    | Statut |
|---|---|---|
| Wave         | CI, SN                  | Stable |
| Orange Money | CI, SN, CM, BF, ML, GN  | Stable |
| MTN MoMo     | CI, GH, CM, BJ, SN, UG  | Stable |
| Moov Money   | CI, BJ, TG, BF, ML, NE  | Stable |

## Installation

```bash
pip install django-mobile-money
```

## Quickstart

### 1. INSTALLED_APPS

```python
INSTALLED_APPS = [
    "django_mobile_money",
]
```

### 2. settings.py

```python
MOBILE_MONEY = {
    "DEFAULT_BACKEND": "wave",
    "WAVE": {
        "API_KEY": env("WAVE_API_KEY"),
        "SANDBOX": True,
    },
    "ORANGE_MONEY": {
        "CLIENT_ID":     env("ORANGE_CLIENT_ID"),
        "CLIENT_SECRET": env("ORANGE_CLIENT_SECRET"),
    },
    "MTN_MOMO": {
        "SUBSCRIPTION_KEY": env("MTN_SUBSCRIPTION_KEY"),
        "ENVIRONMENT":      "sandbox",
    },
    "MOOV_MONEY": {
        "USERNAME":   env("MOOV_USERNAME"),
        "PASSWORD":   env("MOOV_PASSWORD"),
        "PARTNER_ID": env("MOOV_PARTNER_ID"),
    },
}
```

### 3. urls.py

```python
urlpatterns = [
    path("mobile-money/", include("django_mobile_money.urls")),
]
```

### 4. Lancer un paiement

```python
from django_mobile_money import pay

result = pay(
    phone="+22507XXXXXXXX",
    amount=5000,
    backend="wave",
)

if result["status"] == "success":
    print("Paiement confirme :", result["transaction_id"])
elif result["status"] == "pending":
    print("En attente de confirmation")
else:
    print("Echec :", result["message"])
```

## Reponse standardisee

```python
{
    "status":             "pending" | "success" | "failed",
    "transaction_id":     str,
    "provider_reference": str,
    "message":            str,
    "raw_response":       dict,
}
```

## Modeles Django

- MobileTransaction - historique complet des paiements
- WebhookLog - logs des webhooks entrants

## Signals

```python
from django.dispatch import receiver
from django_mobile_money.signals import payment_success

@receiver(payment_success)
def on_payment_success(sender, transaction, backend_id, **kwargs):
    print(f"Paiement reussi : {transaction.transaction_id}")
```

## Template tags

```html
{% load mobile_money_tags %}
{% payment_button phone="+22507XXXXXXXX" amount=5000 backend="wave" %}
{% transaction_status_badge transaction.status %}
```

## Tests

```bash
uv run pytest -v
uv run coverage run -m pytest && uv run coverage report
# 34 tests - 92% coverage
```

## Contribution

Voir CONTRIBUTING.md — les contributions sont les bienvenues !

## Auteur

OURA KONAN ROMEO - Django Developer & IT Instructor
Abidjan, Cote d Ivoire
https://github.com/oura02

## Licence

MIT 2026 OURA KONAN ROMEO
