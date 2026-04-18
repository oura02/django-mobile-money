import hashlib
import hmac
import json
import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import InvalidSignatureError, MobileMoneyError, PaymentTimeoutError


class MoovMoneyBackend(BasePaymentBackend):
    """
    Backend Moov Money / Flooz (CI, BJ, TG, BF, ML, NE, GA).
    """
    backend_id = "moov_money"
    display_name = "Moov Money"
    supported_countries = ["CI", "BJ", "TG", "BF", "ML", "NE", "GA"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("MOOV_MONEY", {})
        self.username   = config.get("USERNAME", "")
        self.password   = config.get("PASSWORD", "")
        self.partner_id = config.get("PARTNER_ID", "")
        self.sandbox    = config.get("SANDBOX", True)
        self.base_url = (
            "https://sandbox.moov-africa.com/api/v1"
            if self.sandbox
            else "https://api.moov-africa.com/api/v1"
        )
        self._token = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        resp = requests.post(
            f"{self.base_url}/auth/token",
            json={"username": self.username, "password": self.password},
            timeout=15,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type":  "application/json",
            "X-Partner-Id":  self.partner_id,
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
            "msisdn":       phone,
            "amount":       str(amount),
            "currency":     currency,
            "externalId":   reference,
            "payerMessage": kwargs.get("description", "Paiement"),
            "payeeNote":    kwargs.get("note", reference),
        }

        try:
            resp = requests.post(
                f"{self.base_url}/collections/request-to-pay",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="moov_money",
                message="Moov Money API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="moov_money",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=data.get("transactionId", ""),
            provider_reference=data.get("financialTransactionId", ""),
            message=data.get("reason", ""),
            raw_response=data,
        )

    def verify_payment(self, transaction_id: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/collections/request-to-pay/{transaction_id}",
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="moov_money",
                message=str(exc),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=transaction_id,
            provider_reference=data.get("financialTransactionId", ""),
            message=data.get("reason", ""),
            raw_response=data,
        )

    def process_webhook(self, payload: dict, headers: dict) -> dict:
        from django.conf import settings
        secret = settings.MOBILE_MONEY.get("MOOV_MONEY", {}).get("WEBHOOK_SECRET", "")

        if secret:
            signature = headers.get("X-Moov-Signature", "")
            body = json.dumps(payload, separators=(",", ":"))
            expected = hmac.new(
                secret.encode(), body.encode(), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected, signature):
                raise InvalidSignatureError(
                    backend="moov_money",
                    message="Signature webhook Moov Money invalide",
                )

        return self._standard_response(
            status=self._map_status(payload.get("status", "")),
            transaction_id=payload.get("transactionId", ""),
            provider_reference=payload.get("financialTransactionId", ""),
            message=payload.get("reason", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "SUCCESSFUL": "success",
            "FAILED":     "failed",
            "CANCELLED":  "failed",
            "PENDING":    "pending",
        }.get(str(raw).upper(), "pending")