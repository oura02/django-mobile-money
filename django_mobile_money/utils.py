import logging

from .models import MobileTransaction
from .signals import payment_failed, payment_pending, payment_success

logger = logging.getLogger("django_mobile_money")


def create_transaction(
    backend_id: str,
    phone: str,
    amount,
    currency: str,
    reference: str,
    result: dict,
) -> MobileTransaction:
    """
    Crée ou met à jour une MobileTransaction depuis le dict standardisé.
    """
    transaction, created = MobileTransaction.objects.update_or_create(
        transaction_id=result["transaction_id"] or reference,
        defaults={
            "backend":            backend_id,
            "phone":              phone,
            "amount":             amount,
            "currency":           currency,
            "reference":          reference,
            "status":             result["status"],
            "provider_reference": result["provider_reference"],
            "message":            result["message"],
            "raw_response":       result["raw_response"],
        },
    )
    _emit_signal(transaction)
    return transaction


def update_transaction(transaction_id: str, result: dict) -> MobileTransaction | None:
    """
    Met à jour le statut d'une transaction existante.
    """
    try:
        transaction = MobileTransaction.objects.get(transaction_id=transaction_id)
        transaction.status             = result["status"]
        transaction.provider_reference = result["provider_reference"]
        transaction.message            = result["message"]
        transaction.raw_response       = result["raw_response"]
        transaction.save()
        _emit_signal(transaction)
        return transaction
    except MobileTransaction.DoesNotExist:
        return None


def _emit_signal(transaction: MobileTransaction):
    """Émet le bon signal selon le statut de la transaction."""
    kwargs = {
        "transaction": transaction,
        "backend_id":  transaction.backend,
    }
    if transaction.status == "success":
        payment_success.send(sender=MobileTransaction, **kwargs)
    elif transaction.status == "failed":
        payment_failed.send(sender=MobileTransaction, **kwargs)
    else:
        payment_pending.send(sender=MobileTransaction, **kwargs)