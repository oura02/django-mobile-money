import base64
import uuid
from datetime import datetime
from decimal import Decimal

import requests

from .base import BasePaymentBackend
from ..exceptions import MobileMoneyError, PaymentTimeoutError


class MPesaBackend(BasePaymentBackend):
    """
    Backend M-Pesa (Safaricom).
    Docs : https://developer.safaricom.co.ke/
    Supporte : KE, TZ, GH
    """
    backend_id = "mpesa"
    display_name = "M-Pesa"
    supported_countries = ["KE", "TZ", "GH"]

    def __init__(self):
        from django.conf import settings
        config = settings.MOBILE_MONEY.get("MPESA", {})
        self.consumer_key    = config.get("CONSUMER_KEY", "")
        self.consumer_secret = config.get("CONSUMER_SECRET", "")
        self.shortcode       = config.get("SHORTCODE", "")
        self.passkey         = config.get("PASSKEY", "")
        self.callback_url    = config.get("CALLBACK_URL", "https://example.com/webhook")
        self.sandbox         = config.get("SANDBOX", True)
        self.base_url = (
            "https://sandbox.safaricom.co.ke"
            if self.sandbox
            else "https://api.safaricom.co.ke"
        )
        self._token = None

    def _get_token(self) -> str:
        if self._token:
            return self._token
        credentials = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()
        resp = requests.get(
            f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",
            headers={"Authorization": f"Basic {credentials}"},
            timeout=15,
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        return self._token

    def _password(self) -> tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        raw = f"{self.shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(raw.encode()).decode()
        return password, timestamp

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type":  "application/json",
        }

    def initiate_payment(
        self,
        phone: str,
        amount: Decimal,
        currency: str = "KES",
        reference: str = "",
        **kwargs,
    ) -> dict:
        if not reference:
            reference = str(uuid.uuid4())[:12]

        password, timestamp = self._password()

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password":          password,
            "Timestamp":         timestamp,
            "TransactionType":   "CustomerPayBillOnline",
            "Amount":            str(int(amount)),
            "PartyA":            phone.lstrip("+"),
            "PartyB":            self.shortcode,
            "PhoneNumber":       phone.lstrip("+"),
            "CallBackURL":       self.callback_url,
            "AccountReference":  reference,
            "TransactionDesc":   kwargs.get("description", "Paiement"),
        }

        try:
            resp = requests.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=self._headers(),
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.Timeout as exc:
            raise PaymentTimeoutError(
                backend="mpesa",
                message="M-Pesa API timeout",
            ) from exc

        except requests.HTTPError as exc:
            raise MobileMoneyError(
                backend="mpesa",
                message=f"Erreur HTTP {exc.response.status_code} : {exc.response.text}",
                code=str(exc.response.status_code),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("ResponseCode", "")),
            transaction_id=data.get("CheckoutRequestID", ""),
            provider_reference=data.get("MerchantRequestID", ""),
            message=data.get("ResponseDescription", ""),
            raw_response=data,
        )

    def verify_payment(self, transaction_id: str) -> dict:
        password, timestamp = self._password()
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password":          password,
            "Timestamp":         timestamp,
            "CheckoutRequestID": transaction_id,
        }
        try:
            resp = requests.post(
                f"{self.base_url}/mpesa/stkpushquery/v1/query",
                json=payload,
                headers=self._headers(),
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

        except requests.RequestException as exc:
            raise MobileMoneyError(
                backend="mpesa",
                message=str(exc),
            ) from exc

        return self._standard_response(
            status=self._map_status(data.get("ResultCode", "")),
            transaction_id=transaction_id,
            provider_reference=data.get("MpesaReceiptNumber", ""),
            message=data.get("ResultDesc", ""),
            raw_response=data,
        )

    def process_webhook(self, payload: dict, headers: dict) -> dict:
        body = payload.get("Body", {}).get("stkCallback", {})
        result_code = str(body.get("ResultCode", "1"))
        items = body.get("CallbackMetadata", {}).get("Item", [])
        receipt = next(
            (i["Value"] for i in items if i.get("Name") == "MpesaReceiptNumber"),
            "",
        )
        return self._standard_response(
            status=self._map_status(result_code),
            transaction_id=body.get("CheckoutRequestID", ""),
            provider_reference=receipt,
            message=body.get("ResultDesc", ""),
            raw_response=payload,
        )

    @staticmethod
    def _map_status(raw: str) -> str:
        return {
            "0":  "success",
            "1":  "failed",
            "17": "failed",
            "26": "failed",
            "32": "failed",
            "1032": "failed",
        }.get(str(raw), "pending")