Modèles
=======

MobileTransaction
-----------------

Historique complet de tous les paiements Mobile Money.

.. code-block:: python

   from django_mobile_money.models import MobileTransaction

   # Toutes les transactions
   transactions = MobileTransaction.objects.all()

   # Filtrer par backend
   wave_transactions = MobileTransaction.objects.filter(backend="wave")

   # Filtrer par statut
   success = MobileTransaction.objects.filter(status="success")

   # Filtrer par téléphone
   user_transactions = MobileTransaction.objects.filter(
       phone="+22507XXXXXXXX"
   )

Champs disponibles
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Champ
     - Type
     - Description
   * - id
     - UUIDField
     - Identifiant unique
   * - transaction_id
     - CharField
     - ID de la transaction
   * - provider_reference
     - CharField
     - Référence du provider
   * - backend
     - CharField
     - Backend utilisé (wave, orange_money...)
   * - phone
     - CharField
     - Numéro de téléphone
   * - amount
     - DecimalField
     - Montant
   * - currency
     - CharField
     - Devise (XOF par défaut)
   * - status
     - CharField
     - pending, success, failed
   * - created_at
     - DateTimeField
     - Date de création

WebhookLog
----------

Logs de tous les webhooks reçus des providers.

.. code-block:: python

   from django_mobile_money.models import WebhookLog

   # Tous les webhooks non traités
   pending = WebhookLog.objects.filter(processed=False)

   # Webhooks d'un backend
   wave_logs = WebhookLog.objects.filter(backend="wave")