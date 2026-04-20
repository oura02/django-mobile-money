Signals
=======

django-mobile-money émet des signaux Django à chaque changement de statut.

Signaux disponibles
-------------------

.. code-block:: python

   from django_mobile_money.signals import (
       payment_success,
       payment_failed,
       payment_pending,
   )

Utilisation
-----------

.. code-block:: python

   from django.dispatch import receiver
   from django_mobile_money.signals import payment_success, payment_failed

   @receiver(payment_success)
   def on_payment_success(sender, transaction, backend_id, **kwargs):
       """Appelé quand un paiement est confirmé."""
       # Mettre à jour la commande
       order = Order.objects.get(reference=transaction.reference)
       order.status = "paid"
       order.save()
       # Envoyer un email de confirmation
       send_confirmation_email(order)

   @receiver(payment_failed)
   def on_payment_failed(sender, transaction, backend_id, **kwargs):
       """Appelé quand un paiement échoue."""
       order = Order.objects.get(reference=transaction.reference)
       order.status = "failed"
       order.save()