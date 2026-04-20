# Contributing to django-mobile-money

Merci de contribuer à django-mobile-money ! 🎉

## Comment contribuer

### 1. Fork et clone

git clone https://github.com/TON_USERNAME/django-mobile-money.git
cd django-mobile-money

### 2. Installe les dépendances

uv sync

### 3. Crée une branche

git checkout -b feat/mon-backend

### 4. Lance les tests

uv run pytest -v
uv run coverage run -m pytest
uv run coverage report

### 5. Ouvre une Pull Request

## Ajouter un nouveau backend

1. Crée `django_mobile_money/backends/mon_backend.py`
2. Hérite de `BasePaymentBackend`
3. Implémente `initiate_payment`, `verify_payment`, `process_webhook`
4. Ajoute le backend dans `backends/__init__.py`
5. Ajoute les tests dans `tests/test_mon_backend.py`

## Standards de code

- Python 3.10+
- Tests obligatoires pour chaque backend
- Coverage minimum 90%
- Docstrings en français ou anglais

## Backends prioritaires

- [ ] Airtel Money (CI, GH, TZ, UG)
- [ ] Free Money (SN)
- [ ] Wizall Money (CI, SN)
- [ ] M-Pesa (KE, TZ, GH)

## Auteur principal

OURA KONAN ROMEO — github.com/oura02