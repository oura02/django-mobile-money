import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import MobileMoneyError, PaymentTimeoutError


class CinetPayBackend(BasePaymentBackend):
    """
    Backend CinetPay.
    Docs : https://docs.cinetpay.com/
    Supporte : CI, SN, CM, BF, TG, ML, GN, GW, CD
    """
    backend_id = "cinetpay"
    display_name = "CinetPay"
    supported_countries = ["CI", "SN", "CM", "BF", "TG", "ML", "GN", "CD"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("CINETPAY", {})
        self.api_key    = config.get("API_KEY", "")
        self.site_id    = config.get("SITE_ID", "")
        self.sandbox    = config.get("SANDBOX", True)
        self.base_url = (
            "https://api-checkout.cinetpay.com/v2"
            if not self.sandbox
            else "https://api-checkout.cinetpay.com/v2"
        )

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
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
            "apikey":           self.api_key,
            "site_id":          self.site_id,
            "transaction_id":   reference,
            "amount":           int(amount),
            "currency":         currency,
            "description":      kwargs.get("description", "Paiement CinetPay"),
            "return_url":       kwargs.get("return_url", "https://example.com/return"),
            "notify_url":       kwargs.get("notify_url", "https://example.com/webhook"),
            "customer_phone_number": phone,
            "channels":         "MOBILE_MONEY",
        }

        try:
            resp = requests.post(
                f"{self.base_url}/payment",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="cinetpay",
                message="CinetPay API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="cinetpay",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        code = str(data.get("code", ""))
        return self._standard_response(
            status=self._map_status(code),
            transaction_id=data.get("data", {}).get("transaction_id", reference),
            provider_reference=data.get("data", {}).get("payment_token", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def verify_payment(self, transaction_id: str) -> dict:
        payload = {
            "apikey":         self.api_key,
            "site_id":        self.site_id,
            "transaction_id": transaction_id,
        }
        try:
            resp = requests.post(
                f"{self.base_url}/payment/check",
                json=payload,
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="cinetpay",
                message=str(exc),
            ) from exc

        return self._standard_response(
            status=self._map_status(str(data.get("code", ""))),
            transaction_id=transaction_id,
            provider_reference=data.get("data", {}).get("payment_token", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def process_webhook(self, payload: dict, headers: dict) -> dict:
        return self._standard_response(
            status=self._map_status(str(payload.get("cpm_result", ""))),
            transaction_id=payload.get("cpm_trans_id", ""),
            provider_reference=payload.get("cpm_payment_id", ""),
            message=payload.get("cpm_error_message", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "00":      "success",
            "600":     "pending",
            "601":     "pending",
            "ACCEPTED": "success",
            "FAILED":   "failed",
            "PENDING":  "pending",
        }.get(str(raw).upper(), "pending")