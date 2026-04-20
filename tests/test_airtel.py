from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from django_mobile_money.backends.airtel_money import AirtelMoneyBackend
from django_mobile_money.exceptions import MobileMoneyError


@pytest.fixture
def backend():
    return AirtelMoneyBackend()


def test_map_status_success(backend):
    assert backend._map_status("TS") == "success"
    assert backend._map_status("SUCCESS") == "success"


def test_map_status_failed(backend):
    assert backend._map_status("TF") == "failed"
    assert backend._map_status("EXPIRED") == "failed"


def test_map_status_pending(backend):
    assert backend._map_status("TIP") == "pending"
    assert backend._map_status("") == "pending"


@patch("django_mobile_money.backends.airtel_money.requests.post")
def test_initiate_payment_success(mock_post, backend):
    mock_token = MagicMock()
    mock_token.json.return_value = {"access_token": "airtel-token"}
    mock_token.raise_for_status = lambda: None

    mock_pay = MagicMock()
    mock_pay.json.return_value = {
        "data": {"transaction": {"id": "airtel_txn_001", "status": "TIP", "airtel_money_id": ""}},
        "status": {"message": "En attente"},
    }
    mock_pay.raise_for_status = lambda: None
    mock_post.side_effect = [mock_token, mock_pay]

    result = backend.initiate_payment(phone="+22507000000", amount=Decimal("3000"))
    assert result["status"] == "pending"
    assert result["transaction_id"] == "airtel_txn_001"


def test_process_webhook(backend):
    payload = {
        "transaction": {
            "id": "airtel_txn_002",
            "status": "TS",
            "airtel_money_id": "AM_001",
            "message": "",
        }
    }
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"