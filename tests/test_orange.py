from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from django_mobile_money.backends.orange_money import OrangeMoneyBackend
from django_mobile_money.exceptions import MobileMoneyError


@pytest.fixture
def backend():
    return OrangeMoneyBackend()


def test_map_status_success(backend):
    assert backend._map_status("SUCCESS") == "success"
    assert backend._map_status("SUCCESSFULL") == "success"


def test_map_status_failed(backend):
    assert backend._map_status("FAILED") == "failed"
    assert backend._map_status("CANCELLED") == "failed"


def test_map_status_pending(backend):
    assert backend._map_status("PENDING") == "pending"
    assert backend._map_status("INITIATED") == "pending"
    assert backend._map_status("") == "pending"


@patch("django_mobile_money.backends.orange_money.requests.post")
def test_initiate_payment_success(mock_post, backend):
    # Mock du token
    mock_token = MagicMock()
    mock_token.json.return_value = {"access_token": "fake-token"}
    mock_token.raise_for_status = lambda: None

    # Mock du paiement
    mock_pay = MagicMock()
    mock_pay.json.return_value = {
        "pay_token":    "tok_abc123",
        "notif_token":  "notif_xyz",
        "status":       "PENDING",
        "message":      "En attente",
    }
    mock_pay.raise_for_status = lambda: None

    mock_post.side_effect = [mock_token, mock_pay]

    result = backend.initiate_payment(
        phone="+22507000000",
        amount=Decimal("2500"),
        reference="cmd_002",
    )

    assert result["status"] == "pending"
    assert result["transaction_id"] == "tok_abc123"


@patch("django_mobile_money.backends.orange_money.requests.post")
def test_initiate_payment_http_error(mock_post, backend):
    import requests as req

    # Mock du token
    mock_token = MagicMock()
    mock_token.json.return_value = {"access_token": "fake-token"}
    mock_token.raise_for_status = lambda: None

    # Mock erreur HTTP
    mock_err = MagicMock(status_code=403, text="Forbidden")
    mock_post.side_effect = [
        mock_token,
        MagicMock(raise_for_status=MagicMock(
            side_effect=req.HTTPError(response=mock_err)
        )),
    ]

    with pytest.raises(MobileMoneyError):
        backend.initiate_payment(phone="+22507000000", amount=Decimal("2500"))


def test_process_webhook(backend):
    payload = {
        "pay_token": "tok_webhook",
        "txnid":     "txn_999",
        "status":    "SUCCESS",
        "message":   "Paiement réussi",
    }
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"
    assert result["transaction_id"] == "tok_webhook"