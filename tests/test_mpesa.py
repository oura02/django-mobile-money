from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from django_mobile_money.backends.mpesa import MPesaBackend
from django_mobile_money.exceptions import MobileMoneyError


@pytest.fixture
def backend():
    return MPesaBackend()


def test_map_status_success(backend):
    assert backend._map_status("0") == "success"


def test_map_status_failed(backend):
    assert backend._map_status("1") == "failed"
    assert backend._map_status("1032") == "failed"


def test_map_status_pending(backend):
    assert backend._map_status("") == "pending"


@patch("django_mobile_money.backends.mpesa.requests.get")
@patch("django_mobile_money.backends.mpesa.requests.post")
def test_initiate_payment_success(mock_post, mock_get, backend):
    mock_get.return_value = MagicMock(
        json=lambda: {"access_token": "mpesa-token"},
        raise_for_status=lambda: None,
    )
    mock_post.return_value = MagicMock(
        json=lambda: {
            "ResponseCode":        "0",
            "CheckoutRequestID":   "mpesa_txn_001",
            "MerchantRequestID":   "merchant_001",
            "ResponseDescription": "Success",
        },
        raise_for_status=lambda: None,
    )
    result = backend.initiate_payment(phone="+254700000000", amount=Decimal("1000"))
    assert result["status"] == "success"
    assert result["transaction_id"] == "mpesa_txn_001"


def test_process_webhook(backend):
    payload = {
        "Body": {
            "stkCallback": {
                "ResultCode": "0",
                "ResultDesc": "Success",
                "CheckoutRequestID": "mpesa_txn_002",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "MpesaReceiptNumber", "Value": "NLJ7RT61SV"},
                    ]
                },
            }
        }
    }
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"
    assert result["provider_reference"] == "NLJ7RT61SV"