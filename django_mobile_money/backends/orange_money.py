import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import InvalidSignatureError, MobileMoneyError, PaymentTimeoutError


class OrangeMoneyBackend(BasePaymentBackend):
    """
    Backend Orange Money (CI, SN, CM, BF, ML, GN, MG).
    Docs : https://developer.orange.com/apis/omccore-ci/
    """
    backend_id = "orange_money"
    display_name = "Orange Money"
    supported_countries = ["CI", "SN", "CM", "BF", "ML", "GN"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("ORANGE_MONEY", {})
        self.client_id     = config.get("CLIENT_ID", "")
        self.client_secret = config.get("CLIENT_SECRET", "")
        self.sandbox       = config.get("SANDBOX", True)
        self.base_url = (
            "https://api.sandbox.orange.com"
            if self.sandbox
            else "https://api.orange.com"
        )
        self._token = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        resp = requests.post(
            f"{self.base_url}/oauth/v3/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     self.client_id,
                "client_secret": self.client_secret,
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
            "Accept":        "application/json",
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
            "merchant_key": self.client_id,
            "currency":     currency,
            "order_id":     reference,
            "amount":       str(amount),
            "return_url":   kwargs.get("return_url", "https://example.com/return"),
            "cancel_url":   kwargs.get("cancel_url", "https://example.com/cancel"),
            "notif_url":    kwargs.get("notif_url", "https://example.com/webhook"),
            "lang":         kwargs.get("lang", "fr"),
            "reference":    reference,
        }

        try:
            resp = requests.post(
                f"{self.base_url}/orange-money-webpay/CI/v1/webpayment",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="orange_money",
                message="Orange Money API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="orange_money",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=data.get("pay_token", ""),
            provider_reference=data.get("notif_token", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def verify_payment(self, transaction_id: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/orange-money-webpay/CI/v1/transactionstatus",
                params={"order_id": transaction_id},
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="orange_money",
                message=str(exc),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("status", "")),
            transaction_id=transaction_id,
            provider_reference=data.get("txnid", ""),
            message=data.get("message", ""),
            raw_response=data,
        )

    def process_webhook(self, payload: dict, headers: dict) -> dict:
        return self._standard_response(
            status=self._map_status(payload.get("status", "")),
            transaction_id=payload.get("pay_token", ""),
            provider_reference=payload.get("txnid", ""),
            message=payload.get("message", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "SUCCESS":    "success",
            "SUCCESSFULL": "success",
            "FAILED":     "failed",
            "CANCELLED":  "failed",
            "PENDING":    "pending",
            "INITIATED":  "pending",
        }.get(str(raw).upper(), "pending")