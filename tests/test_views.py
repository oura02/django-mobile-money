import json
from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory

from django_mobile_money.views import WebhookView


@pytest.fixture
def factory():
    return RequestFactory()


def make_request(factory, payload):
    return factory.post(
        "/webhooks/wave/",
        data=json.dumps(payload),
        content_type="application/json",
    )


@patch("django_mobile_money.views.update_transaction")
@patch("django_mobile_money.views.WebhookLog.objects.create")
def test_webhook_wave_success(mock_log, mock_update, factory):
    mock_log.return_value = MagicMock(save=lambda: None)
    mock_update.return_value = MagicMock()

    payload = {
        "id":             "txn_test_001",
        "payment_status": "succeeded",
        "wave_launch_url": "",
    }

    request  = make_request(factory, payload)
    view     = WebhookView.as_view(backend_id="wave")
    response = view(request)

    assert response.status_code == 200


@patch("django_mobile_money.views.WebhookLog.objects.create")
def test_webhook_invalid_json(mock_log, factory):
    mock_log.return_value = MagicMock(save=lambda: None)

    request = factory.post(
        "/webhooks/wave/",
        data="invalid json",
        content_type="application/json",
    )
    view     = WebhookView.as_view(backend_id="wave")
    response = view(request)

    assert response.status_code == 400


@patch("django_mobile_money.views.WebhookLog.objects.create")
def test_webhook_unknown_backend(mock_log, factory):
    mock_log.return_value = MagicMock(save=lambda: None)

    payload  = {"id": "txn_001", "status": "SUCCESSFUL"}
    request  = make_request(factory, payload)
    view     = WebhookView.as_view(backend_id="backend_inexistant")
    response = view(request)

    assert response.status_code == 500