import hashlib
import hmac
import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import InvalidSignatureError, MobileMoneyError, PaymentTimeoutError


class WaveBackend(BasePaymentBackend):
    """
    Backend Wave CI / Wave SN.
    Docs : https://docs.wave.com/
    """
    backend_id = "wave"
    display_name = "Wave"
    supported_countries = ["CI", "SN"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("WAVE", {})
        self.api_key  = config.get("API_KEY", "")
        self.sandbox  = config.get("SANDBOX", True)
        self.base_url = (
            "https://api.sandbox.wave.com/v1"
            if self.sandbox
            else "https://api.wave.com/v1"
        )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------ #
    # PAIEMENT                                                             #
    # ------------------------------------------------------------------ #
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
            "currency":    currency,
            "amount":      str(amount),
            "error_url":   kwargs.get("error_url", "https://example.com/error"),
            "success_url": kwargs.get("success_url", "https://example.com/success"),
            "client_reference": reference,
        }

        # Si numéro fourni → paiement USSD push direct
        if phone:
            payload["receive_amount"] = str(amount)
            payload["mobile"]         = phone

        try:
            resp = requests.post(
                f"{self.base_url}/checkout/sessions",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="wave",
                message="Wave API timeout après 30s",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="wave",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("payment_status", "pending")),
            transaction_id=data.get("id", ""),
            provider_reference=data.get("wave_launch_url", ""),
            message=data.get("payment_status", ""),
            raw_response=data,
        )

    # ------------------------------------------------------------------ #
    # VÉRIFICATION                                                         #
    # ------------------------------------------------------------------ #
    def verify_payment(self, transaction_id: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/checkout/sessions/{transaction_id}",
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="wave",
                message=str(exc),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("payment_status", "pending")),
            transaction_id=transaction_id,
            provider_reference=data.get("wave_launch_url", ""),
            message=data.get("payment_status", ""),
            raw_response=data,
        )

    # ------------------------------------------------------------------ #
    # WEBHOOK                                                              #
    # ------------------------------------------------------------------ #
    def process_webhook(self, payload: dict, headers: dict) -> dict:
        from django.conf import settings
        secret = settings.MOBILE_MONEY.get("WAVE", {}).get("WEBHOOK_SECRET", "")

        if secret:
            import json
            signature = headers.get("Wave-Signature", "")
            body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            expected = hmac.new(
                secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected, signature):
                raise InvalidSignatureError(
                    backend="wave",
                    message="Signature webhook Wave invalide",
                )

        return self._standard_response(
            status=self._map_status(payload.get("payment_status", "pending")),
            transaction_id=payload.get("id", ""),
            provider_reference=payload.get("wave_launch_url", ""),
            message=payload.get("payment_status", ""),
            raw_response=payload,
        )

    # ------------------------------------------------------------------ #
    # UTILS                                                                #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "succeeded":  "success",
            "failed":     "failed",
            "cancelled":  "failed",
            "processing": "pending",
            "pending":    "pending",
        }.get(raw.lower() if raw else "", "pending")