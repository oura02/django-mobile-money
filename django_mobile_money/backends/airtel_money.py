import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import MobileMoneyError, PaymentTimeoutError


class AirtelMoneyBackend(BasePaymentBackend):
    """
    Backend Airtel Money.
    Docs : https://developers.airtel.africa/
    Supporte : CI, GH, TZ, UG, ZM, KE, MG, CD, CG, GA, MW, NE, RW, TD
    """
    backend_id = "airtel_money"
    display_name = "Airtel Money"
    supported_countries = ["CI", "GH", "TZ", "UG", "ZM", "KE", "MG", "CD"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("AIRTEL_MONEY", {})
        self.client_id     = config.get("CLIENT_ID", "")
        self.client_secret = config.get("CLIENT_SECRET", "")
        self.country       = config.get("COUNTRY", "CI")
        self.currency      = config.get("CURRENCY", "XOF")
        self.sandbox       = config.get("SANDBOX", True)
        self.base_url = (
            "https://openapiuat.airtel.africa"
            if self.sandbox
            else "https://openapi.airtel.africa"
        )
        self._token = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        resp = requests.post(
            f"{self.base_url}/auth/oauth2/token",
            json={
                "client_id":     self.client_id,
                "client_secret": self.client_secret,
                "grant_type":    "client_credentials",
            },
            timeout=15,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type":  "application/json",
            "Accept":        "*/*",
            "X-Country":     self.country,
            "X-Currency":    self.currency,
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
            "reference": reference,
            "subscriber": {
                "country":  self.country,
                "currency": currency,
                "msisdn":   phone.lstrip("+"),
            },
            "transaction": {
                "amount":   str(amount),
                "country":  self.country,
                "currency": currency,
                "id":       reference,
            },
        }

        try:
            resp = requests.post(
                f"{self.base_url}/merchant/v2/payments/",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="airtel_money",
                message="Airtel Money API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="airtel_money",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        status_data = data.get("data", {}).get("transaction", {})
        return self._standard_response(
            status=self._map_status(status_data.get("status", "")),
            transaction_id=status_data.get("id", reference),
            provider_reference=status_data.get("airtel_money_id", ""),
            message=data.get("status", {}).get("message", ""),
            raw_response=data,
        )

    def verify_payment(self, transaction_id: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/standard/v1/payments/{transaction_id}",
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="airtel_money",
                message=str(exc),
            ) from exc

        status_data = data.get("data", {}).get("transaction", {})
        return self._standard_response(
            status=self._map_status(status_data.get("status", "")),
            transaction_id=transaction_id,
            provider_reference=status_data.get("airtel_money_id", ""),
            message=data.get("status", {}).get("message", ""),
            raw_response=data,
        )

    def process_webhook(self, payload: dict, headers: dict) -> dict:
        transaction = payload.get("transaction", {})
        return self._standard_response(
            status=self._map_status(transaction.get("status", "")),
            transaction_id=transaction.get("id", ""),
            provider_reference=transaction.get("airtel_money_id", ""),
            message=transaction.get("message", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "TS":      "success",   # Transaction Successful
            "TF":      "failed",    # Transaction Failed
            "TA":      "pending",   # Transaction Ambiguous
            "TIP":     "pending",   # Transaction In Progress
            "EXPIRED": "failed",
            "SUCCESS": "success",
            "FAILED":  "failed",
            "PENDING": "pending",
        }.get(str(raw).upper(), "pending")