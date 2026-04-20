django-mobile-money
===================

.. image:: https://badge.fury.io/py/django-mobile-money.svg
   :target: https://badge.fury.io/py/django-mobile-money

.. image:: https://img.shields.io/badge/coverage-90%25-brightgreen
   :target: https://github.com/oura02/django-mobile-money

Package Django réutilisable pour les paiements Mobile Money africains.
Intégrez **10 providers** en 3 lignes de code.

.. code-block:: python

   from django_mobile_money import pay

   result = pay(phone="+22507XXXXXXXX", amount=5000, backend="wave")

   if result["status"] == "success":
       print("Paiement confirmé !")

Providers supportés
-------------------

.. list-table::
   :header-rows: 1

   * - Provider
     - Pays
     - Statut
   * - Wave
     - CI, SN
     - Stable
   * - Orange Money
     - CI, SN, CM, BF, ML, GN
     - Stable
   * - MTN MoMo
     - CI, GH, CM, BJ, SN, UG
     - Stable
   * - Moov Money
     - CI, BJ, TG, BF, ML, NE
     - Stable
   * - Airtel Money
     - CI, GH, TZ, UG, ZM, KE
     - Stable
   * - Free Money
     - SN
     - Stable
   * - M-Pesa
     - KE, TZ, GH
     - Stable
   * - Wizall Money
     - CI, SN, BF, ML
     - Stable
   * - Celtiis Cash
     - BJ, TG
     - Stable
   * - YAS Money
     - CI
     - Stable

.. toctree::
   :maxdepth: 2
   :caption: Guide

   installation
   quickstart
   backends
   models
   signals
   webhooks
   contributing