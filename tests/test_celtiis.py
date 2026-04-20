from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from django_mobile_money.backends.celtiis_cash import CeltiisCashBackend
from django_mobile_money.exceptions import MobileMoneyError

@pytest.fixture
def backend():
    return CeltiisCashBackend()

def test_map_status_success(backend):
    assert backend._map_status("SUCCESS") == "success"
    assert backend._map_status("SUCCESSFUL") == "success"

def test_map_status_failed(backend):
    assert backend._map_status("FAILED") == "failed"
    assert backend._map_status("CANCELLED") == "failed"

def test_map_status_pending(backend):
    assert backend._map_status("PENDING") == "pending"
    assert backend._map_status("") == "pending"

@patch("django_mobile_money.backends.celtiis_cash.requests.post")
def test_initiate_payment_success(mock_post, backend):
    mock_post.return_value = MagicMock(
        json=lambda: {"transactionId": "celtiis_001", "celtiisRef": "ref_001", "status": "PENDING", "message": ""},
        raise_for_status=lambda: None,
    )
    result = backend.initiate_payment(phone="+22990000000", amount=Decimal("1500"))
    assert result["status"] == "pending"
    assert result["transaction_id"] == "celtiis_001"

def test_process_webhook(backend):
    payload = {"transactionId": "celtiis_002", "celtiisRef": "ref_002", "status": "SUCCESS", "message": ""}
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"