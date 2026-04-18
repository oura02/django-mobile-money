import base64
import uuid
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import MobileMoneyError, PaymentTimeoutError


class MTNMoMoBackend(BasePaymentBackend):
    """
    Backend MTN Mobile Money (Collections API v1).
    Docs : https://momodeveloper.mtn.com/
    """
    backend_id = "mtn_momo"
    display_name = "MTN MoMo"
    supported_countries = ["CI", "GH", "CM", "BJ", "SN", "GN", "ZM", "UG"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("MTN_MOMO", {})
        self.subscription_key = config.get("SUBSCRIPTION_KEY", "")
        self.api_user         = config.get("API_USER", str(uuid.uuid4()))
        self.api_key          = config.get("API_KEY", "")
        self.environment      = config.get("ENVIRONMENT", "sandbox")
        self.base_url = (
            "https://sandbox.momodeveloper.mtn.com"
            if self.environment == "sandbox"
            else "https://proxy.momoapi.mtn.com"
        )
        self._token = None

    def _get_token(self) -> str:
        if self._token:
            return self._token

        credentials = base64.b64encode(
            f"{self.api_user}:{self.api_key}".encode()
        ).decode()

        resp = requests.post(
            f"{self.base_url}/collection/token/",
            headers={
                "Authorization":        f"Basic {credentials}",
                "Ocp-Apim-Subscription-Key": self.subscription_key,
            },
            timeout=15,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def _headers(self, reference_id: str = "") -> dict:
        h = {
            "Authorization":             f"Bearer {self._get_token()}",
            "X-Target-Environment":      self.environment,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type":              "application/json",
        }
        if reference_id:
            h["X-Reference-Id"] = reference_id
        return h

    def initiate_payment(
        self,
        phone: str,
        amount: Decimal,
        currency: str = "EUR",   # MTN sandbox utilise EUR
        reference: str = "",
        **kwargs,
    ) -> dict:
        reference_id = str(uuid.uuid4())

        payload = {
            "amount":       str(amount),
            "currency":     currency,
            "externalId":   reference or reference_id,
            "payer": {
                "partyIdType": "MSISDN",
                "partyId":     phone.lstrip("+"),
            },
            "payerMessage": kwargs.get("description", "Paiement"),
            "payeeNote":    kwargs.get("note", reference or reference_id),
        }

        try:
            resp = requests.post(
                f"{self.base_url}/collection/v1_0/requesttopay",
                json=payload,
                headers=self._headers(reference_id=reference_id),
                timeout=30,
            )
            resp.raise_for_status()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="mtn_momo",
                message="MTN MoMo API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="mtn_momo",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        # MTN retourne 202 Accepted + reference_id (pas de body JSON)
        return self._standard_response(
            status="pending",
            transaction_id=reference_id,
            provider_reference=reference_id,
            message="Request to pay envoyé",
            raw_response={"reference_id": reference_id},
        )

    def verify_payment(self, transaction_id: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/collection/v1_0/requesttopay/{transaction_id}",
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="mtn_momo",
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
        return self._standard_response(
            status=self._map_status(payload.get("status", "")),
            transaction_id=payload.get("referenceId", ""),
            provider_reference=payload.get("financialTransactionId", ""),
            message=payload.get("reason", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "SUCCESSFUL": "success",
            "FAILED":     "failed",
            "REJECTED":   "failed",
            "TIMEOUT":    "failed",
            "PENDING":    "pending",
        }.get(str(raw).upper(), "pending")