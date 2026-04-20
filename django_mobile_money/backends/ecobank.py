import base64
import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import MobileMoneyError, PaymentTimeoutError


class EcobankBackend(BasePaymentBackend):
    """
    Backend Ecobank Mobile Money.
    Docs : https://developer.ecobank.com/
    Supporte : CI, GH, TG, BJ, SN, CM, BF, ML, NE, GN, CD, CG
    """
    backend_id = "ecobank"
    display_name = "Ecobank"
    supported_countries = ["CI", "GH", "TG", "BJ", "SN", "CM", "BF", "ML", "NE", "GN"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("ECOBANK", {})
        self.client_id     = config.get("CLIENT_ID", "")
        self.client_secret = config.get("CLIENT_SECRET", "")
        self.merchant_id   = config.get("MERCHANT_ID", "")
        self.country       = config.get("COUNTRY", "CI")
        self.sandbox       = config.get("SANDBOX", True)
        self.base_url = (
            "https://api.sandbox.ecobank.com"
            if self.sandbox
            else "https://api.ecobank.com"
        )
        self._token = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        resp = requests.post(
            f"{self.base_url}/oauth/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type":  "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
            timeout=15,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type":  "application/json",
            "X-Country":     self.country,
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
            "merchantId":    self.merchant_id,
            "transactionId": reference,
            "amount":        str(amount),
            "currency":      currency,
            "phone":         phone,
            "country":       self.country,
            "description":   kwargs.get("description", "Paiement Ecobank"),
            "callbackUrl":   kwargs.get("callback_url", ""),
        }

        try:
            resp = requests.post(
                f"{self.base_url}/v2/momo/payment/request",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="ecobank",
                message="Ecobank API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="ecobank",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=data.get("transactionId", reference),
            provider_reference=data.get("ecobankRef", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def verify_payment(self, transaction_id: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/v2/momo/payment/status/{transaction_id}",
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="ecobank",
                message=str(exc),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=transaction_id,
            provider_reference=data.get("ecobankRef", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def process_webhook(self, payload: dict, headers: dict) -> dict:
        return self._standard_response(
            status=self._map_status(payload.get("status", "")),
            transaction_id=payload.get("transactionId", ""),
            provider_reference=payload.get("ecobankRef", ""),
            message=payload.get("message", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "SUCCESS":    "success",
            "SUCCESSFUL": "success",
            "COMPLETED":  "success",
            "FAILED":     "failed",
            "CANCELLED":  "failed",
            "EXPIRED":    "failed",
            "PENDING":    "pending",
            "INITIATED":  "pending",
            "PROCESSING": "pending",
        }.get(str(raw).upper(), "pending")