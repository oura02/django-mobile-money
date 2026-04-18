# django-mobile-money

> Django reusable package for African mobile money payments.
> Integrez Wave, Orange Money, MTN MoMo et Moov Money en 3 lignes de code.

## Backends supportes

| Provider | Pays | Statut |
|---|---|---|
| Wave | CI, SN | Stable |
| Orange Money | CI, SN, CM, BF, ML, GN | Stable |
| MTN MoMo | CI, GH, CM, BJ, SN, UG | Stable |
| Moov Money | CI, BJ, TG, BF, ML, NE | Stable |

## Installation

```bash
pip install django-mobile-money
```bash

## Quickstart

**1. INSTALLED_APPS**

```python
INSTALLED_APPS = [
    'django_mobile_money',
]
```python

**2. settings.py**

```python
MOBILE_MONEY = {
    'DEFAULT_BACKEND': 'wave',
    'WAVE': {'API_KEY': env('WAVE_API_KEY'), 'SANDBOX': True},
    'ORANGE_MONEY': {'CLIENT_ID': env('ORANGE_CLIENT_ID'), 'CLIENT_SECRET': env('ORANGE_CLIENT_SECRET')},
    'MTN_MOMO': {'SUBSCRIPTION_KEY': env('MTN_SUBSCRIPTION_KEY'), 'ENVIRONMENT': 'sandbox'},
    'MOOV_MONEY': {'USERNAME': env('MOOV_USERNAME'), 'PASSWORD': env('MOOV_PASSWORD'), 'PARTNER_ID': env('MOOV_PARTNER_ID')},
}
```python

**3. Lancer un paiement**

```python
from django_mobile_money import pay

result = pay(phone='+22507XXXXXXXX', amount=5000, backend='wave')

if result['status'] == 'success':
    print('Paiement confirme :', result['transaction_id'])
```python

## Tests

```bash
uv run pytest -v  # 26 passed
```bash

## Auteur

OURA KONAN ROMEO - Django Developer & IT Instructor
Abidjan, Cote d Ivoire
https://github.com/oura02

## Licence

MIT 2026 OURA KONAN ROMEO
