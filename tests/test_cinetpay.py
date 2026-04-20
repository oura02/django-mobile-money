from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from django_mobile_money.backends.cinetpay import CinetPayBackend
from django_mobile_money.exceptions import MobileMoneyError

@pytest.fixture
def backend():
    return CinetPayBackend()

def test_map_status_success(backend):
    assert backend._map_status("00") == "success"
    assert backend._map_status("ACCEPTED") == "success"

def test_map_status_failed(backend):
    assert backend._map_status("FAILED") == "failed"

def test_map_status_pending(backend):
    assert backend._map_status("600") == "pending"
    assert backend._map_status("") == "pending"

@patch("django_mobile_money.backends.cinetpay.requests.post")
def test_initiate_payment_success(mock_post, backend):
    mock_post.return_value = MagicMock(
        json=lambda: {
            "code": "201",
            "message": "CREATED",
            "data": {"transaction_id": "cinet_001", "payment_token": "tok_001"},
        },
        raise_for_status=lambda: None,
    )
    result = backend.initiate_payment(phone="+22507000000", amount=Decimal("5000"))
    assert result["transaction_id"] == "cinet_001"

def test_process_webhook(backend):
    payload = {
        "cpm_trans_id":      "cinet_002",
        "cpm_payment_id":    "pay_002",
        "cpm_result":        "00",
        "cpm_error_message": "",
    }
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"