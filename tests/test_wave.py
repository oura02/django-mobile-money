from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from django_mobile_money.backends.wave import WaveBackend
from django_mobile_money.exceptions import MobileMoneyError


@pytest.fixture
def backend():
    return WaveBackend()


def test_map_status_success(backend):
    assert backend._map_status("succeeded") == "success"


def test_map_status_failed(backend):
    assert backend._map_status("failed") == "failed"


def test_map_status_unknown(backend):
    assert backend._map_status("") == "pending"


@patch("django_mobile_money.backends.wave.requests.post")
def test_initiate_payment_success(mock_post, backend):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "id": "txn_123",
            "payment_status": "pending",
            "wave_launch_url": "https://pay.wave.com/abc",
        },
    )
    mock_post.return_value.raise_for_status = lambda: None

    result = backend.initiate_payment(
        phone="+22507000000",
        amount=Decimal("5000"),
        reference="cmd_001",
    )

    assert result["status"] == "pending"
    assert result["transaction_id"] == "txn_123"


@patch("django_mobile_money.backends.wave.requests.post")
def test_initiate_payment_http_error(mock_post, backend):
    import requests as req
    mock_resp = MagicMock(status_code=401, text="Unauthorized")
    mock_post.return_value.raise_for_status.side_effect = req.HTTPError(
        response=mock_resp
    )

    with pytest.raises(MobileMoneyError):
        backend.initiate_payment(
            phone="+22507000000",
            amount=Decimal("5000"),
        )


def test_process_webhook_no_secret(backend):
    payload = {
        "id": "txn_456",
        "payment_status": "succeeded",
        "wave_launch_url": "",
    }
    result = backend.process_webhook(payload=payload, headers={})
    assert result["status"] == "success"
    assert result["transaction_id"] == "txn_456"