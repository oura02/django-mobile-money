Backends
========

Chaque backend hérite de ``BasePaymentBackend`` et implémente
3 méthodes : ``initiate_payment``, ``verify_payment``, ``process_webhook``.

Wave
----

.. code-block:: python

   MOBILE_MONEY = {
       "WAVE": {
           "API_KEY": env("WAVE_API_KEY"),
           "SANDBOX": True,
           "WEBHOOK_SECRET": env("WAVE_WEBHOOK_SECRET", default=""),
       },
   }

**Pays supportés** : CI, SN

Orange Money
------------

.. code-block:: python

   MOBILE_MONEY = {
       "ORANGE_MONEY": {
           "CLIENT_ID":     env("ORANGE_CLIENT_ID"),
           "CLIENT_SECRET": env("ORANGE_CLIENT_SECRET"),
           "SANDBOX":       True,
       },
   }

**Pays supportés** : CI, SN, CM, BF, ML, GN

MTN MoMo
--------

.. code-block:: python

   MOBILE_MONEY = {
       "MTN_MOMO": {
           "SUBSCRIPTION_KEY": env("MTN_SUBSCRIPTION_KEY"),
           "API_USER":         env("MTN_API_USER"),
           "API_KEY":          env("MTN_API_KEY"),
           "ENVIRONMENT":      "sandbox",
       },
   }

**Pays supportés** : CI, GH, CM, BJ, SN, UG

Moov Money
----------

.. code-block:: python

   MOBILE_MONEY = {
       "MOOV_MONEY": {
           "USERNAME":       env("MOOV_USERNAME"),
           "PASSWORD":       env("MOOV_PASSWORD"),
           "PARTNER_ID":     env("MOOV_PARTNER_ID"),
           "WEBHOOK_SECRET": env("MOOV_WEBHOOK_SECRET", default=""),
           "SANDBOX":        True,
       },
   }

**Pays supportés** : CI, BJ, TG, BF, ML, NE

Airtel Money
------------

.. code-block:: python

   MOBILE_MONEY = {
       "AIRTEL_MONEY": {
           "CLIENT_ID":     env("AIRTEL_CLIENT_ID"),
           "CLIENT_SECRET": env("AIRTEL_CLIENT_SECRET"),
           "COUNTRY":       "CI",
           "CURRENCY":      "XOF",
           "SANDBOX":       True,
       },
   }

**Pays supportés** : CI, GH, TZ, UG, ZM, KE, MG, CD

M-Pesa
------

.. code-block:: python

   MOBILE_MONEY = {
       "MPESA": {
           "CONSUMER_KEY":    env("MPESA_CONSUMER_KEY"),
           "CONSUMER_SECRET": env("MPESA_CONSUMER_SECRET"),
           "SHORTCODE":       env("MPESA_SHORTCODE"),
           "PASSKEY":         env("MPESA_PASSKEY"),
           "CALLBACK_URL":    env("MPESA_CALLBACK_URL"),
           "SANDBOX":         True,
       },
   }

**Pays supportés** : KE, TZ, GH

Ajouter un backend custom
--------------------------

.. code-block:: python

   from django_mobile_money.backends.base import BasePaymentBackend

   class MonBackend(BasePaymentBackend):
       backend_id        = "mon_backend"
       display_name      = "Mon Provider"
       supported_countries = ["CI"]

       def initiate_payment(self, phone, amount, currency="XOF", reference="", **kwargs):
           return self._standard_response(
               status="pending",
               transaction_id="txn_001",
           )

       def verify_payment(self, transaction_id):
           ...

       def process_webhook(self, payload, headers):
           ...