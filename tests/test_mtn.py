from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from django_mobile_money.backends.mtn_momo import MTNMoMoBackend
from django_mobile_money.exceptions import MobileMoneyError


@pytest.fixture
def backend():
    return MTNMoMoBackend()


def test_map_status_success(backend):
    assert backend._map_status("SUCCESSFUL") == "success"


def test_map_status_failed(backend):
    assert backend._map_status("FAILED") == "failed"
    assert backend._map_status("REJECTED") == "failed"
    assert backend._map_status("TIMEOUT") == "failed"


def test_map_status_pending(backend):
    assert backend._map_status("PENDING") == "pending"
    assert backend._map_status("") == "pending"


@patch("django_mobile_money.backends.mtn_momo.requests.post")
def test_initiate_payment_returns_pending(mock_post, backend):
    # MTN retourne 202 sans body JSON — juste raise_for_status OK
    mock_post.return_value = MagicMock(
        status_code=202,
        raise_for_status=lambda: None,
    )

    result = backend.initiate_payment(
        phone="+22507000000",
        amount=Decimal("10000"),
        reference="cmd_mtn_001",
    )

    assert result["status"] == "pending"
    assert result["transaction_id"] != ""  # UUID généré


@patch("django_mobile_money.backends.mtn_momo.requests.post")
def test_initiate_payment_http_error(mock_post, backend):
    import requests as req
    mock_err = MagicMock(status_code=401, text="Unauthorized")
    mock_post.return_value.raise_for_status.side_effect = req.HTTPError(
        response=mock_err
    )

    with pytest.raises(MobileMoneyError):
        backend.initiate_payment(phone="+22507000000", amount=Decimal("5000"))


@patch("django_mobile_money.backends.mtn_momo.requests.post")
@patch("django_mobile_money.backends.mtn_momo.requests.get")
def test_verify_payment(mock_get, mock_post, backend):
    mock_post.return_value = MagicMock(
        json=lambda: {"access_token": "tok"},
        raise_for_status=lambda: None,
    )
    mock_get.return_value = MagicMock(
        json=lambda: {
            "status":                  "SUCCESSFUL",
            "financialTransactionId":  "fin_123",
            "reason":                  "",
        },
        raise_for_status=lambda: None,
    )

    result = backend.verify_payment("uuid-ref-123")
    assert result["status"] == "success"
    assert result["provider_reference"] == "fin_123"


def test_process_webhook(backend):
    payload = {
        "status":                 "SUCCESSFUL",
        "referenceId":            "ref_001",
        "financialTransactionId": "fin_001",
        "reason":                 "",
    }
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"
    assert result["transaction_id"] == "ref_001"