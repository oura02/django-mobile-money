from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from django_mobile_money.backends.yas_money import YASMoneyBackend
from django_mobile_money.exceptions import MobileMoneyError

@pytest.fixture
def backend():
    return YASMoneyBackend()

def test_map_status_success(backend):
    assert backend._map_status("SUCCESS") == "success"
    assert backend._map_status("COMPLETED") == "success"

def test_map_status_failed(backend):
    assert backend._map_status("FAILED") == "failed"
    assert backend._map_status("EXPIRED") == "failed"

def test_map_status_pending(backend):
    assert backend._map_status("PENDING") == "pending"
    assert backend._map_status("") == "pending"

@patch("django_mobile_money.backends.yas_money.requests.post")
def test_initiate_payment_success(mock_post, backend):
    mock_post.return_value = MagicMock(
        json=lambda: {"transaction_id": "yas_001", "yas_ref": "ref_001", "status": "PENDING", "message": ""},
        raise_for_status=lambda: None,
    )
    result = backend.initiate_payment(phone="+22507000000", amount=Decimal("3000"))
    assert result["status"] == "pending"
    assert result["transaction_id"] == "yas_001"

def test_process_webhook(backend):
    payload = {"transaction_id": "yas_002", "yas_ref": "ref_002", "status": "SUCCESS", "message": ""}
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"