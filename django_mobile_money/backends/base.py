from abc import ABC, abstractmethod
from decimal import Decimal


class BasePaymentBackend(ABC):
    """
    Classe abstraite dont héritent tous les backends Mobile Money.
    """
    backend_id: str = ""
    display_name: str = ""
    supported_countries: list[str] = []

    @abstractmethod
    def initiate_payment(
        self,
        phone: str,
        amount: Decimal,
        currency: str = "XOF",
        reference: str = "",
        **kwargs,
    ) -> dict:
        """
        Lance un paiement. Retourne toujours ce dict standardisé :
        {
            "status":               "pending" | "success" | "failed",
            "transaction_id":       str,
            "provider_reference":   str,
            "message":              str,
            "raw_response":         dict,
        }
        """
        raise NotImplementedError

    @abstractmethod
    def verify_payment(self, transaction_id: str) -> dict:
        """Vérifie le statut d'une transaction existante."""
        raise NotImplementedError

    @abstractmethod
    def process_webhook(self, payload: dict, headers: dict) -> dict:
        """Traite un webhook entrant du provider."""
        raise NotImplementedError

    def _standard_response(
        self,
        status: str,
        transaction_id: str = "",
        provider_reference: str = "",
        message: str = "",
        raw_response: dict = None,
    ) -> dict:
        """Construit le dict de réponse standardisé."""
        return {
            "status": status,
            "transaction_id": transaction_id,
            "provider_reference": provider_reference,
            "message": message,
            "raw_response": raw_response or {},
        }