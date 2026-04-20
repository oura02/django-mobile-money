Quickstart
==========

Paiement simple
---------------

.. code-block:: python

   from django_mobile_money import pay

   # Paiement Wave
   result = pay(
       phone="+22507XXXXXXXX",
       amount=5000,
       backend="wave",
   )

   if result["status"] == "success":
       print("Paiement confirmé :", result["transaction_id"])
   elif result["status"] == "pending":
       print("En attente de confirmation")
   else:
       print("Échec :", result["message"])

Réponse standardisée
--------------------

Tous les backends retournent le même format :

.. code-block:: python

   {
       "status":             "pending" | "success" | "failed",
       "transaction_id":     str,
       "provider_reference": str,
       "message":            str,
       "raw_response":       dict,
   }

Vérifier une transaction
------------------------

.. code-block:: python

   from django_mobile_money.backends import BACKENDS

   backend = BACKENDS["wave"]()
   result  = backend.verify_payment("txn_abc123")
   print(result["status"])

Utiliser le modèle MobileTransaction
-------------------------------------

.. code-block:: python

   from django_mobile_money.models import MobileTransaction

   # Toutes les transactions
   transactions = MobileTransaction.objects.all()

   # Transactions réussies Wave
   wave_success = MobileTransaction.objects.filter(
       backend="wave",
       status="success",
   )

   # Dernière transaction d'un numéro
   last = MobileTransaction.objects.filter(
       phone="+22507XXXXXXXX"
   ).first()