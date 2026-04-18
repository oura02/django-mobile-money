from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from django_mobile_money.backends.moov_money import MoovMoneyBackend
from django_mobile_money.exceptions import InvalidSignatureError, MobileMoneyError


@pytest.fixture
def backend():
    return MoovMoneyBackend()


def test_map_status_success(backend):
    assert backend._map_status("SUCCESSFUL") == "success"


def test_map_status_failed(backend):
    assert backend._map_status("FAILED") == "failed"
    assert backend._map_status("CANCELLED") == "failed"


def test_map_status_pending(backend):
    assert backend._map_status("PENDING") == "pending"
    assert backend._map_status("") == "pending"


@patch("django_mobile_money.backends.moov_money.requests.post")
def test_initiate_payment_success(mock_post, backend):
    mock_token = MagicMock()
    mock_token.json.return_value = {"access_token": "moov-token"}
    mock_token.raise_for_status = lambda: None

    mock_pay = MagicMock()
    mock_pay.json.return_value = {
        "transactionId":          "moov_txn_001",
        "financialTransactionId": "fin_moov_001",
        "status":                 "PENDING",
        "reason":                 "",
    }
    mock_pay.raise_for_status = lambda: None

    mock_post.side_effect = [mock_token, mock_pay]

    result = backend.initiate_payment(
        phone="+22507000000",
        amount=Decimal("3000"),
        reference="cmd_moov_001",
    )

    assert result["status"] == "pending"
    assert result["transaction_id"] == "moov_txn_001"


@patch("django_mobile_money.backends.moov_money.requests.post")
def test_initiate_payment_http_error(mock_post, backend):
    import requests as req

    mock_token = MagicMock()
    mock_token.json.return_value = {"access_token": "moov-token"}
    mock_token.raise_for_status = lambda: None

    mock_err = MagicMock(status_code=500, text="Server Error")
    mock_post.side_effect = [
        mock_token,
        MagicMock(raise_for_status=MagicMock(
            side_effect=req.HTTPError(response=mock_err)
        )),
    ]

    with pytest.raises(MobileMoneyError):
        backend.initiate_payment(phone="+22507000000", amount=Decimal("3000"))


def test_process_webhook_no_secret(backend):
    payload = {
        "transactionId":          "moov_txn_002",
        "financialTransactionId": "fin_002",
        "status":                 "SUCCESSFUL",
        "reason":                 "",
    }
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"
    assert result["transaction_id"] == "moov_txn_002"


def test_process_webhook_invalid_signature(backend):
    from django.conf import settings
    settings.MOBILE_MONEY["MOOV_MONEY"]["WEBHOOK_SECRET"] = "mon-secret"

    payload = {"transactionId": "x", "status": "SUCCESSFUL"}
    with pytest.raises(InvalidSignatureError):
        backend.process_webhook(
            payload=payload,
            headers={"X-Moov-Signature": "mauvaise-signature"},
        )

    # Nettoyage
    settings.MOBILE_MONEY["MOOV_MONEY"]["WEBHOOK_SECRET"] = ""