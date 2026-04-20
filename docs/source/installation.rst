Installation
============

Prérequis
---------

* Python 3.10+
* Django 4.2+

Installation via pip
--------------------

.. code-block:: bash

   pip install django-mobile-money

Installation via uv
-------------------

.. code-block:: bash

   uv add django-mobile-money

Configuration
-------------

Ajoutez ``django_mobile_money`` à vos ``INSTALLED_APPS`` :

.. code-block:: python

   INSTALLED_APPS = [
       ...
       "django_mobile_money",
   ]

Ajoutez la configuration dans ``settings.py`` :

.. code-block:: python

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
       "AIRTEL_MONEY": {
           "CLIENT_ID":     env("AIRTEL_CLIENT_ID"),
           "CLIENT_SECRET": env("AIRTEL_CLIENT_SECRET"),
           "COUNTRY":       "CI",
       },
       "FREE_MONEY": {
           "API_KEY":     env("FREE_API_KEY"),
           "MERCHANT_ID": env("FREE_MERCHANT_ID"),
       },
       "MPESA": {
           "CONSUMER_KEY":    env("MPESA_CONSUMER_KEY"),
           "CONSUMER_SECRET": env("MPESA_CONSUMER_SECRET"),
           "SHORTCODE":       env("MPESA_SHORTCODE"),
           "PASSKEY":         env("MPESA_PASSKEY"),
           "CALLBACK_URL":    env("MPESA_CALLBACK_URL"),
       },
       "WIZALL_MONEY": {
           "API_KEY":     env("WIZALL_API_KEY"),
           "MERCHANT_ID": env("WIZALL_MERCHANT_ID"),
       },
       "CELTIIS_CASH": {
           "API_KEY":     env("CELTIIS_API_KEY"),
           "MERCHANT_ID": env("CELTIIS_MERCHANT_ID"),
           "COUNTRY":     "BJ",
       },
       "YAS_MONEY": {
           "API_KEY":     env("YAS_API_KEY"),
           "MERCHANT_ID": env("YAS_MERCHANT_ID"),
       },
   }

Migrations
----------

.. code-block:: bash

   python manage.py migrate