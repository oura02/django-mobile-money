Webhooks
========

Configuration des URLs
----------------------

.. code-block:: python

   # urls.py
   from django.urls import path, include

   urlpatterns = [
       path("mobile-money/", include("django_mobile_money.urls")),
   ]

Endpoints disponibles
---------------------

.. code-block:: text

   POST /mobile-money/webhooks/wave/
   POST /mobile-money/webhooks/orange-money/
   POST /mobile-money/webhooks/mtn-momo/
   POST /mobile-money/webhooks/moov-money/

Vue personnalisée
-----------------

.. code-block:: python

   from django_mobile_money.views import WebhookView

   urlpatterns = [
       path(
           "webhooks/wave/",
           WebhookView.as_view(backend_id="wave"),
           name="webhook-wave",
       ),
   ]