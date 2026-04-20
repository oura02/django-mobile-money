import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import MobileMoneyError, PaymentTimeoutError


class YASMoneyBackend(BasePaymentBackend):
    """
    Backend YAS Money (Côte d'Ivoire).
    Supporte : CI
    """
    backend_id = "yas_money"
    display_name = "YAS Money"
    supported_countries = ["CI"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("YAS_MONEY", {})
        self.api_key     = config.get("API_KEY", "")
        self.merchant_id = config.get("MERCHANT_ID", "")
        self.sandbox     = config.get("SANDBOX", True)
        self.base_url = (
            "https://sandbox.yas.ci/api/v1"
            if self.sandbox
            else "https://api.yas.ci/api/v1"
        )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
            "X-Merchant-Id": self.merchant_id,
        }

    def initiate_payment(
        self,
        phone: str,
        amount: Decimal,
        currency: str = "XOF",
        reference: str = "",
        **kwargs,
    ) -> dict:
        if not reference:
            reference = str(uuid.uuid4())

        payload = {
            "phone":        phone,
            "amount":       str(amount),
            "currency":     currency,
            "reference":    reference,
            "description":  kwargs.get("description", "Paiement YAS Money"),
            "redirect_url": kwargs.get("redirect_url", ""),
        }

        try:
            resp = requests.post(
                f"{self.base_url}/payment/initiate",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="yas_money",
                message="YAS Money API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="yas_money",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=data.get("transaction_id", ""),
            provider_reference=data.get("yas_ref", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def verify_payment(self, transaction_id: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/payment/status/{transaction_id}",
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="yas_money",
                message=str(exc),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=transaction_id,
            provider_reference=data.get("yas_ref", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def process_webhook(self, payload: dict, headers: dict) -> dict:
        return self._standard_response(
            status=self._map_status(payload.get("status", "")),
            transaction_id=payload.get("transaction_id", ""),
            provider_reference=payload.get("yas_ref", ""),
            message=payload.get("message", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "SUCCESS":    "success",
            "COMPLETED":  "success",
            "FAILED":     "failed",
            "CANCELLED":  "failed",
            "EXPIRED":    "failed",
            "PENDING":    "pending",
            "INITIATED":  "pending",
            "PROCESSING": "pending",
        }.get(str(raw).upper(), "pending")