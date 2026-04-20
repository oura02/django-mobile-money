from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from django_mobile_money.utils import create_transaction, update_transaction, _emit_signal


@pytest.fixture
def mock_result():
    return {
        "status":             "pending",
        "transaction_id":     "txn_util_001",
        "provider_reference": "prov_001",
        "message":            "En attente",
        "raw_response":       {},
    }


@patch("django_mobile_money.utils.MobileTransaction.objects.update_or_create")
def test_create_transaction_pending(mock_uoc, mock_result):
    mock_transaction = MagicMock()
    mock_transaction.status  = "pending"
    mock_transaction.backend = "wave"
    mock_uoc.return_value = (mock_transaction, True)

    result = create_transaction(
        backend_id="wave",
        phone="+22507000000",
        amount=Decimal("5000"),
        currency="XOF",
        reference="cmd_001",
        result=mock_result,
    )

    assert result == mock_transaction
    mock_uoc.assert_called_once()


@patch("django_mobile_money.utils.MobileTransaction.objects.update_or_create")
def test_create_transaction_success(mock_uoc, mock_result):
    mock_transaction = MagicMock()
    mock_transaction.status  = "success"
    mock_transaction.backend = "wave"
    mock_uoc.return_value = (mock_transaction, False)

    mock_result["status"] = "success"
    result = create_transaction(
        backend_id="wave",
        phone="+22507000000",
        amount=Decimal("5000"),
        currency="XOF",
        reference="cmd_002",
        result=mock_result,
    )
    assert result == mock_transaction


@patch("django_mobile_money.utils.MobileTransaction.objects.get")
def test_update_transaction_success(mock_get):
    mock_transaction = MagicMock()
    mock_transaction.status  = "success"
    mock_transaction.backend = "wave"
    mock_get.return_value = mock_transaction

    result = update_transaction("txn_001", {
        "status":             "success",
        "provider_reference": "prov_001",
        "message":            "",
        "raw_response":       {},
    })

    assert result == mock_transaction
    mock_transaction.save.assert_called_once()


@patch("django_mobile_money.utils.MobileTransaction.objects.get")
def test_update_transaction_not_found(mock_get):
    from django_mobile_money.models import MobileTransaction
    mock_get.side_effect = MobileTransaction.DoesNotExist

    result = update_transaction("txn_inexistant", {
        "status":             "failed",
        "provider_reference": "",
        "message":            "",
        "raw_response":       {},
    })

    assert result is None


@patch("django_mobile_money.utils.MobileTransaction.objects.update_or_create")
def test_create_transaction_failed(mock_uoc, mock_result):
    mock_transaction = MagicMock()
    mock_transaction.status  = "failed"
    mock_transaction.backend = "wave"
    mock_uoc.return_value = (mock_transaction, True)

    mock_result["status"] = "failed"
    result = create_transaction(
        backend_id="wave",
        phone="+22507000000",
        amount=Decimal("5000"),
        currency="XOF",
        reference="cmd_003",
        result=mock_result,
    )
    assert result == mock_transaction