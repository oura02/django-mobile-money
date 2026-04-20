from django.urls import path
from .views import WebhookView

app_name = "django_mobile_money"

urlpatterns = [
    path(
        "webhooks/wave/",
        WebhookView.as_view(backend_id="wave"),
        name="webhook-wave",
    ),
    path(
        "webhooks/orange-money/",
        WebhookView.as_view(backend_id="orange_money"),
        name="webhook-orange-money",
    ),
    path(
        "webhooks/mtn-momo/",
        WebhookView.as_view(backend_id="mtn_momo"),
        name="webhook-mtn-momo",
    ),
    path(
        "webhooks/moov-money/",
        WebhookView.as_view(backend_id="moov_money"),
        name="webhook-moov-money",
    ),
]