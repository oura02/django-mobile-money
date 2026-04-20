from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from django_mobile_money.backends.ecobank import EcobankBackend

@pytest.fixture
def backend():
    return EcobankBackend()

def test_map_status_success(backend):
    assert backend._map_status("SUCCESS") == "success"
    assert backend._map_status("COMPLETED") == "success"

def test_map_status_failed(backend):
    assert backend._map_status("FAILED") == "failed"
    assert backend._map_status("CANCELLED") == "failed"

def test_map_status_pending(backend):
    assert backend._map_status("PENDING") == "pending"
    assert backend._map_status("") == "pending"

@patch("django_mobile_money.backends.ecobank.requests.post")
def test_initiate_payment_success(mock_post, backend):
    mock_token = MagicMock()
    mock_token.json.return_value = {"access_token": "eco-token"}
    mock_token.raise_for_status = lambda: None

    mock_pay = MagicMock()
    mock_pay.json.return_value = {
        "transactionId": "eco_001",
        "ecobankRef":    "ref_001",
        "status":        "PENDING",
        "message":       "",
    }
    mock_pay.raise_for_status = lambda: None
    mock_post.side_effect = [mock_token, mock_pay]

    result = backend.initiate_payment(phone="+22507000000", amount=Decimal("4000"))
    assert result["status"] == "pending"
    assert result["transaction_id"] == "eco_001"

def test_process_webhook(backend):
    payload = {"transactionId": "eco_002", "ecobankRef": "ref_002", "status": "SUCCESS", "message": ""}
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"